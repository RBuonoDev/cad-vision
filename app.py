"""Academic parametric part modeller, independently implemented."""
import copy
import json

import streamlit as st
import streamlit.components.v1 as components

from engine import EXAMPLE, ModelError, build, dumps, export_model, loads, mesh
from viewer import html

st.set_page_config(page_title='CAD Acadêmico', page_icon='📐', layout='wide')
st.title('CAD Acadêmico · Modelagem de peças')
st.caption('Protótipo independente: esboços cotados, extrusões, cortes e histórico editável. Unidade: mm.')


@st.cache_data(show_spinner=False, max_entries=8)
def compile_project(serialized):
    model, history = build(loads(serialized))
    box = model.val().BoundingBox()
    return dict(mesh=mesh(model), history=history, volume=model.val().Volume(),
                size=[box.xlen, box.ylen, box.zlen],
                step=export_model(model, 'STEP'), stl=export_model(model, 'STL'))


def commit(candidate):
    compile_project(dumps(candidate))
    st.session_state.features = candidate
    st.session_state.revision += 1


st.session_state.setdefault('features', copy.deepcopy(EXAMPLE))
st.session_state.setdefault('revision', 0)
features = st.session_state.features
rev = st.session_state.revision

with st.sidebar:
    st.subheader('Projeto')
    st.info('Perfis no plano XY, posicionados em uma altura Z. Extrusões avançam em +Z; cortes em −Z.')
    if st.button('Carregar exemplo'):
        st.session_state.features = copy.deepcopy(EXAMPLE)
        st.session_state.revision += 1
        st.rerun()
    uploaded = st.file_uploader('Abrir projeto JSON', type=['json'])
    if st.button('Importar projeto', disabled=uploaded is None):
        try:
            commit(loads(uploaded.getvalue()))
            st.rerun()
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
    st.divider()
    st.subheader('Árvore de operações')
    for index, f in enumerate(features):
        action = 'Extrusão' if f['operation'] == 'add' else 'Corte'
        st.write(f"{index + 1}. {'●' if f['enabled'] else '○'} {f['name']} · {action}")
    st.caption('A ordem define a reconstrução. Um erro não substitui a última versão válida.')

editor, display = st.columns([1, 1.8], gap='large')
with editor:
    st.subheader('Esboço e operação')
    mode = st.radio('Modo', ['Nova operação', 'Editar operação'], horizontal=True)
    index = None
    if mode == 'Editar operação':
        index = st.selectbox('Operação', range(len(features)),
                             format_func=lambda i: f"{i+1}. {features[i]['name']}", key=f'pick_{rev}')
    default = (features[index] if index is not None else
               dict(name=f'Operação {len(features)+1}', operation='cut', profile='circle',
                    x=0, y=0, z=20, length=20, width=20, diameter=10, depth=20, enabled=True))
    form_key = f'{rev}_{mode}_{index}'
    # Profile selector is outside the form so the dimension labels update immediately.
    profile_label = st.selectbox('Perfil fechado', ['Retângulo', 'Círculo'],
                                index=0 if default['profile'] == 'rectangle' else 1,
                                key=f'profile_{form_key}')
    with st.form(f'feature_{form_key}_{profile_label}'):
        name = st.text_input('Nome', value=default['name'], max_chars=80)
        operation = st.selectbox('Operação geométrica', ['Extrusão (+Z)', 'Corte (−Z)'],
                                 index=0 if default['operation'] == 'add' else 1)
        a, b = st.columns(2)
        x = a.number_input('Centro X', -10000.0, 10000.0, float(default['x']))
        y = b.number_input('Centro Y', -10000.0, 10000.0, float(default['y']))
        length, width, diameter = default['length'], default['width'], default['diameter']
        if profile_label == 'Retângulo':
            length = a.number_input('Comprimento X', 0.1, 10000.0, float(length))
            width = b.number_input('Largura Y', 0.1, 10000.0, float(width))
        else:
            diameter = st.number_input('Diâmetro', 0.1, 10000.0, float(diameter))
        z = a.number_input('Plano Z', -10000.0, 10000.0, float(default['z']))
        depth = b.number_input('Profundidade', 0.1, 10000.0, float(default['depth']))
        enabled = st.checkbox('Operação ativa', value=default['enabled'])
        submit = st.form_submit_button('Reconstruir peça', type='primary')
    candidate_feature = dict(name=name.strip(), operation='add' if operation.startswith('Extrusão') else 'cut',
                             profile='rectangle' if profile_label == 'Retângulo' else 'circle',
                             x=x, y=y, z=z, length=length, width=width, diameter=diameter,
                             depth=depth, enabled=enabled)
    if submit:
        candidate = copy.deepcopy(features)
        if index is None:
            candidate.append(candidate_feature)
        else:
            candidate[index] = candidate_feature
        try:
            with st.spinner('Reconstruindo operações e verificando o sólido…'):
                commit(candidate)
            st.rerun()
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))

    st.caption('Prévia do perfil do formulário. Só “Reconstruir peça” aplica a alteração ao sólido.')
    sx, sy = (length, width) if profile_label == 'Retângulo' else (diameter, diameter)
    scale = 210 / max(sx, sy)
    w, h = sx * scale, sy * scale
    outline = (f'<rect x="{150-w/2}" y="{145-h/2}" width="{w}" height="{h}"/>'
               if profile_label == 'Retângulo' else f'<circle cx="150" cy="145" r="{w/2}"/>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 290" role="img" aria-label="Perfil cotado">
    <rect width="300" height="290" fill="#101e30"/><g stroke="#59728d" stroke-dasharray="5 5"><path d="M150 20V265M20 145H280"/></g>
    <g stroke="#36b8fa" fill="#173b56" stroke-width="2">{outline}</g>
    <g fill="#e0ecff" font-family="sans-serif" font-size="12"><text x="20" y="20">Plano XY · Z = {z:g} mm</text>
    <text x="20" y="260">{'X × Y' if profile_label == 'Retângulo' else 'Ø'}: {sx:g}{(' × '+format(sy,'g')) if profile_label == 'Retângulo' else ''} mm</text>
    <text x="20" y="280">Centro ({x:g}, {y:g}) mm</text></g></svg>'''
    st.image(svg, width=300)

with display:
    try:
        with st.spinner('Preparando o modelo geométrico…'):
            result = compile_project(dumps(st.session_state.features))
        st.subheader('Modelo sólido 3D')
        components.html(html(result['mesh']), height=530, scrolling=False)
        a, b = st.columns(2)
        a.metric('Volume', f"{result['volume']:,.2f} mm³")
        b.metric('Dimensões totais X × Y × Z', ' × '.join(f'{v:g}' for v in result['size'])+' mm')
        st.dataframe(result['history'], hide_index=True)
        st.subheader('Salvar e exportar')
        a, b, c = st.columns(3)
        a.download_button('Projeto editável', dumps(st.session_state.features), 'projeto.json', 'application/json')
        b.download_button('Sólido STEP', result['step'], 'peca.step', 'application/octet-stream')
        c.download_button('Malha STL', result['stl'], 'peca.stl', 'application/octet-stream')
        st.caption('JSON preserva o histórico deste protótipo. STEP transfere a geometria; STL contém a malha sem unidade explícita (coordenadas em mm).')
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))

st.caption('Escopo inicial: um único sólido, retângulos e círculos em planos XY. Sem desenho livre, solver de restrições, montagem ou leitura de arquivos SLDPRT.')

