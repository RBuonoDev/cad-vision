"""Interface CAD 2D → 3D (protótipo para placas/blocos retangulares com um furo)."""
import io
import json
import math

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps
from google import genai
from google.genai import types

st.set_page_config(page_title="CAD Vision | Desenho 2D para 3D", page_icon="📐", layout="wide", initial_sidebar_state="expanded")

DEFAULTS = {
    "comprimento": 100.0,
    "largura": 60.0,
    "altura": 25.0,
    "furo_diametro": 16.0,
    "furo_x": 50.0,
    "furo_y": 30.0,
}
for key, val in DEFAULTS.items():
    st.session_state.setdefault(key, val)
st.session_state.setdefault("observacao", "")
st.session_state.setdefault("cotas_ia", [])

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html,body,[class*="css"],.stApp {font-family:'DM Sans',sans-serif;}
.stApp {background:#0b1220;color:#e8eef9;}
[data-testid="stHeader"] {background:rgba(11,18,32,.80);}
[data-testid="stSidebar"] {background:#111c30;border-right:1px solid #263752;}
[data-testid="stSidebar"] * {color:#e4edfa;}
.block-container {max-width:1600px;padding-top:1.65rem;padding-bottom:3rem;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.025em;}
h1 {font-size:2.15rem!important;margin-bottom:.15rem!important;}
h3 {font-size:1.1rem!important;}
[data-testid="stFileUploader"] {border:1px dashed #47739b;border-radius:12px;padding:.6rem;background:#131f33;}
[data-testid="stMetric"] {background:#142238;border:1px solid #2a3d56;border-radius:12px;padding:12px 16px;}
[data-testid="stMetricLabel"] {color:#9fb5d0;}
[data-testid="stMetricValue"] {font-family:'Space Grotesk',sans-serif;font-size:1.3rem;}
.stButton>button[kind="primary"] {background:#17a5ea;border:0;color:#071421;font-weight:700;border-radius:9px;}
.stButton>button {border-radius:9px;font-weight:600;}
[data-testid="stTabs"] button {font-weight:700;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-color:#30435e!important;background:#121d30;border-radius:15px;}
section[data-testid="stSidebar"] .stTextInput input {background:#0b1729;}
small,.stCaption {color:#9eb1ca!important;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ◈ CAD VISION")
    st.caption("Painel de projeto • Protótipo 1.1")
    st.divider()
    st.subheader("⚙️ Inteligência artificial")
    api_key = st.text_input("Chave de API do Gemini", type="password", placeholder="Cole sua chave aqui")
    st.caption("A chave é usada para analisar a imagem. Sem ela, o editor 3D continua funcionando.")
    st.divider()
    st.subheader("🎛️ Aparência do modelo")
    color = st.color_picker("Cor da peça", value="#3AA8F2")
    wireframe = st.toggle("Exibir contornos", value=True)
    show_grid = st.toggle("Exibir grade", value=True)
    show_axes = st.toggle("Exibir eixos", value=True)
    st.divider()
    st.info("**Escopo desta versão:** peça retangular maciça com até um furo circular passante vertical. Não é um reconstrutor CAD universal.")

st.title("📐 Desenho técnico 2D → Modelo 3D")
st.caption("Carregue seu desenho, interprete as cotas com IA, ajuste dimensões e inspecione o sólido em tempo real.")

with st.container(border=True):
    top_left, top_right = st.columns([2.3, 1], gap="large")
    with top_left:
        uploaded_file = st.file_uploader("01 · Importe um desenho mecânico", type=["png", "jpg", "jpeg"], help="Foto ou imagem de desenho técnico em PNG ou JPG.")
    with top_right:
        st.write("**02 · Interpretar cotas**")
        analyze = st.button("⚡ Analisar desenho com IA", type="primary", use_container_width=True, disabled=(uploaded_file is None or not api_key))
        if uploaded_file is None:
            st.caption("Faça upload de uma imagem para habilitar.")
        elif not api_key:
            st.caption("Informe a chave Gemini no painel lateral.")

image = None
if uploaded_file is not None:
    try:
        image = ImageOps.exif_transpose(Image.open(io.BytesIO(uploaded_file.getvalue()))).convert("RGB")
    except Exception as exc:
        st.error(f"Arquivo de imagem inválido: {exc}")

if analyze and image is not None:
    prompt = """
Analise esta imagem de desenho técnico mecânico. Retorne SOMENTE JSON.
Você está extraindo dimensões para um protótipo que suporta apenas um prisma retangular
com no máximo um furo circular passante perpendicular à face superior.
O JSON deve ter as chaves comprimento, largura, altura, furo_diametro, furo_x,
furo_y e observacao. Unidade: milímetros.
furo_x e furo_y representam a distância do centro do furo às bordas esquerda
(X) e inferior (Y) da face superior do retângulo.
Para toda cota não indicada claramente, use null, nunca estime por proporções.
Para peça claramente sem furo, furo_diametro=0.
No campo observacao, informe ambiguidade, unidade não confirmada ou geometria
fora do escopo (por exemplo, eixos, engrenagens, chanfros, múltiplos furos).
Não invente dados e não confunda vista isométrica com vista superior.
"""
    with st.spinner("Interpretando o desenho com Gemini..."):
        try:
            buff = io.BytesIO()
            image.save(buff, format="PNG")
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, types.Part.from_bytes(data=buff.getvalue(), mime_type="image/png")],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            parsed = json.loads(response.text)
            detected, unconfirmed = [], []
            for key in DEFAULTS:
                raw = parsed.get(key)
                if isinstance(raw, bool) or raw is None:
                    unconfirmed.append(key)
                    continue
                try:
                    value = float(raw)
                except (TypeError, ValueError):
                    unconfirmed.append(key)
                    continue
                if not math.isfinite(value) or value < 0 or (key in ("comprimento", "largura", "altura") and value <= 0):
                    unconfirmed.append(key)
                    continue
                st.session_state[key] = value
                detected.append(key)
            st.session_state.cotas_ia = detected
            st.session_state.observacao = str(parsed.get("observacao") or "")
            if detected:
                st.success("Cotas extraídas: " + ", ".join(detected) + ".")
            if unconfirmed:
                st.warning("Revise manualmente as cotas não confirmadas: " + ", ".join(unconfirmed) + ".")
        except Exception as exc:
            st.error(f"Não foi possível concluir a análise: {exc}")

visual_tab, data_tab = st.tabs(["🧊  Visualização e edição", "📊  Dados e exportação"])

with visual_tab:
    left, right = st.columns([0.94, 1.35], gap="large")
    with left:
        with st.container(border=True):
            st.subheader("📷 Desenho original")
            if image is None:
                st.info("Nenhum desenho importado. Experimente as cotas de exemplo ou envie uma imagem acima.")
            else:
                st.image(image, use_container_width=True)
                st.caption(f"Imagem: {image.width} × {image.height} pixels")
            if st.session_state.observacao:
                st.warning("**Observação da IA:** " + st.session_state.observacao)

        with st.container(border=True):
            st.subheader("✏️ Editar cotas")
            st.caption("03 · Altere qualquer dimensão (mm). O modelo será redesenhado automaticamente.")
            a, b = st.columns(2)
            with a:
                length = st.number_input("Comprimento X (mm)", min_value=0.1, step=1.0, format="%.2f", key="comprimento")
                width = st.number_input("Largura Y (mm)", min_value=0.1, step=1.0, format="%.2f", key="largura")
                height = st.number_input("Altura Z (mm)", min_value=0.1, step=1.0, format="%.2f", key="altura")
            with b:
                diameter = st.number_input("Diâmetro do furo (mm)", min_value=0.0, step=1.0, format="%.2f", key="furo_diametro")
                hole_x = st.number_input("Centro do furo • X (mm)", min_value=0.0, step=1.0, format="%.2f", key="furo_x")
                hole_y = st.number_input("Centro do furo • Y (mm)", min_value=0.0, step=1.0, format="%.2f", key="furo_y")
            if st.button("↺ Restaurar dimensões de exemplo", use_container_width=True):
                for key, value in DEFAULTS.items():
                    st.session_state[key] = value
                st.rerun()

    with right:
        radius = diameter / 2
        valid_hole = diameter == 0 or (
            hole_x - radius >= 0 and hole_x + radius <= length
            and hole_y - radius >= 0 and hole_y + radius <= width
        )
        with st.container(border=True):
            st.subheader("🧊 Visualizador 3D interativo")
            st.caption("Arraste para girar · Scroll para zoom · Botão direito para deslocar")
            if not valid_hole:
                st.error("O furo ultrapassa as bordas do bloco. Ajuste a posição ou o diâmetro.")
            else:
                params = json.dumps({
                    "length": length, "width": width, "height": height,
                    "diameter": diameter, "holeX": hole_x, "holeY": hole_y,
                    "wireframe": wireframe, "grid": show_grid, "axes": show_axes,
                    "color": color,
                }, allow_nan=False)
                html = r'''<!doctype html><html lang="pt-br"><head><meta charset="utf-8" />
<style>
*{box-sizing:border-box}body{margin:0;background:#0c1628;font-family:Arial,sans-serif;color:#cfddf5;overflow:hidden}
#viewport{position:absolute;inset:0}#help{position:absolute;left:16px;top:14px;padding:9px 12px;background:#13223aee;border:1px solid #34506f;border-radius:10px;font-size:12px;pointer-events:none}
#legend{position:absolute;bottom:14px;left:16px;color:#90a9cd;font-size:12px}
</style><script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head><body><div id="viewport"></div><div id="help">VISTA ISOMÉTRICA · mm</div><div id="legend">X: comprimento &nbsp; • &nbsp; Y: largura &nbsp; • &nbsp; Z: altura</div>
<script>
const p=__PARAMS__;
const host=document.querySelector('#viewport');
const scene=new THREE.Scene();scene.background=new THREE.Color('#0c1628');
const camera=new THREE.PerspectiveCamera(43,1,.001,1000000);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputEncoding=THREE.sRGBEncoding;host.appendChild(renderer.domElement);
const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;
const shape=new THREE.Shape();shape.moveTo(-p.length/2,-p.width/2);shape.lineTo(p.length/2,-p.width/2);shape.lineTo(p.length/2,p.width/2);shape.lineTo(-p.length/2,p.width/2);shape.closePath();
if(p.diameter>0){const h=new THREE.Path();h.absarc(p.holeX-p.length/2,p.holeY-p.width/2,p.diameter/2,0,2*Math.PI,true);shape.holes.push(h)}
const geo=new THREE.ExtrudeGeometry(shape,{depth:p.height,bevelEnabled:false,steps:1,curveSegments:80});geo.rotateX(-Math.PI/2);geo.translate(0,-p.height/2,0);geo.computeVertexNormals();
const surface=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:p.color,metalness:.22,roughness:.36,side:THREE.DoubleSide}));scene.add(surface);
if(p.wireframe){const edges=new THREE.LineSegments(new THREE.EdgesGeometry(geo,15),new THREE.LineBasicMaterial({color:0x0b2b49}));scene.add(edges)}
scene.add(new THREE.HemisphereLight(0xf7fbff,0x556b8b,2));const sunlight=new THREE.DirectionalLight(0xffffff,2.2);sunlight.position.set(2,3,4);scene.add(sunlight);
const size=Math.max(p.length,p.width,p.height);
if(p.grid){const grid=new THREE.GridHelper(size*2.8,24,0x496383,0x243a56);grid.position.y=-p.height/2-.4;scene.add(grid)}
if(p.axes){const axes=new THREE.AxesHelper(size*.45);axes.position.set(-p.length*.68,-p.height/2,-p.width*.7);scene.add(axes)}
camera.position.set(size*1.45,size*1.1,size*1.55);camera.near=Math.max(size/1000,.001);camera.far=size*100;camera.updateProjectionMatrix();controls.target.set(0,0,0);controls.update();
function resize(){const w=host.clientWidth||800,h=host.clientHeight||540;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}window.addEventListener('resize',resize);resize();
function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera)}animate();
</script></body></html>'''.replace("__PARAMS__", params)
                components.html(html, height=545, scrolling=False)
                st.caption("Modelo geométrico real de bloco com furo passante; visualização ilustrativa, não análise estrutural CAE.")
        if valid_hole:
            volume = (length * width - math.pi * (diameter / 2) ** 2) * height
            m1, m2, m3 = st.columns(3)
            m1.metric("Volume", f"{volume:,.1f} mm³")
            m2.metric("Comprimento", f"{length:g} mm")
            m3.metric("Furo", "Sem furo" if diameter == 0 else f"Ø {diameter:g} mm")

with data_tab:
    st.subheader("Dados do projeto")
    data = {key: float(st.session_state[key]) for key in DEFAULTS}
    data["unidade"] = "mm"
    st.json(data)
    st.download_button("⬇️ Exportar cotas (JSON)", data=json.dumps(data, indent=2, ensure_ascii=False), file_name="cotas_cad_vision.json", mime="application/json")
    st.markdown("**Dimensões interpretadas pela IA:** " + (", ".join(st.session_state.cotas_ia) if st.session_state.cotas_ia else "nenhuma análise realizada"))
    st.info("A exportação atual contém parâmetros, não arquivos CAD STEP/STL. A conversão de geometrias arbitrárias exige um motor de CAD paramétrico e verificação humana.")

st.caption("⚠️ Confira sempre todas as cotas no desenho original. Não utilize este protótipo como única base para fabricação ou análise de segurança.")
