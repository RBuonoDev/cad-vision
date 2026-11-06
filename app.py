from pathlib import Path
import re

import streamlit as st


st.set_page_config(page_title="3DE — Estúdio CAD", page_icon="🧊", layout="wide")

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp { background: #070c12; }
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], footer { display: none !important; }
    .block-container { max-width: none !important; padding: 0 !important; }
    [data-testid="stElementContainer"]:has(iframe) {
        width: 100% !important; max-width: none !important;
    }
    iframe {
        display: block; border: 0; width: 100% !important;
        min-width: 0 !important; margin: 0 auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

static_dir = Path(__file__).parent / "static" / "3de"
document = (static_dir / "index.html").read_text(encoding="utf-8")
runtime_path = next(static_dir.glob("solidcraft-web-*.js"))
styles_path = next(static_dir.glob("loading-*.css"))
runtime = runtime_path.read_text(encoding="utf-8")
styles = styles_path.read_text(encoding="utf-8")
build_id = runtime_path.stem.rsplit("-", 1)[-1]
module_start = document.index('<script type="module">') + len('<script type="module">')
module_end = document.index("</script>", module_start)
loader = document[module_start:module_end]
loader = loader.replace(
    f"import init, * as bindings from './{runtime_path.name}';",
    runtime + "\nconst init = __wbg_init; const bindings = {};",
)
loader = re.sub(
    r"const wasm = await init\(\{ module_or_path: '[^']+\.wasm' \}\);",
    f"""if ('serviceWorker' in navigator) {{
  const registrations = await navigator.serviceWorker.getRegistrations();
  await Promise.all(registrations.map(registration => registration.unregister()));
}}
if ('caches' in window) {{
  const names = await caches.keys();
  await Promise.all(names.map(name => caches.delete(name)));
}}
const compressed = await fetch('./engine.wasm.gz?build={build_id}', {{cache: 'no-store'}});
if (!compressed.ok || !compressed.body) throw new Error('Não foi possível carregar o motor 3D.');
const stream = compressed.body.pipeThrough(new DecompressionStream('gzip'));
const wasmResponse = new Response(stream, {{headers: {{'Content-Type': 'application/wasm'}}}});
const initializedWasm = await init({{ module_or_path: wasmResponse }});""",
    loader,
    count=1,
)
loader = loader.replace("{detail: {wasm}}", "{detail: {wasm: initializedWasm}}")
document = document[:module_start] + loader + document[module_end:]
document = re.sub(
    r'<link rel="stylesheet" href="\./loading-[^"]+\.css"[^>]*>',
    f"<style>{styles}</style>",
    document,
    count=1,
)
document = document.replace("<head>", '<head><base href="app/static/3de/">', 1)
document = re.sub(r'<link rel="preload" href="[^\"]+\.wasm"[^>]*>', "", document)
# Streamlit already owns online updates. A nested service worker would keep an obsolete CAD
# engine after deployment, so the embedded app always loads the build identified above.
document = document.replace('if ("serviceWorker" in navigator)', 'if (false && "serviceWorker" in navigator)')
st.components.v1.html(document, height=920, scrolling=False)
