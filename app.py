"""Independent browser CAD workspace. Units: mm."""
import copy
import hashlib

from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from engine import EXAMPLE, ModelError, build, dumps, export_model, loads, mesh, validate
from viewer import html
from constraints import solve_points, ConstraintError

st.set_page_config(page_title='3DE · Modelagem paramétrica', page_icon='◈', layout='wide')
st.markdown('''<style>
:root{color-scheme:dark}.stApp{background:#0c151d}header[data-testid="stHeader"]{background:#0c151dee}
.block-container{padding-top:3.6rem;padding-bottom:1rem;max-width:1800px}
[data-testid="stSidebar"]{background:#12212b;border-right:1px solid #29404a}
h1{font-size:1.7rem!important;letter-spacing:-.04em}h3{font-size:1.03rem!important}
[data-testid="stMetricValue"]{font-size:1.2rem}.brand{font-size:11px;letter-spacing:3px;color:#69d8b9;margin-bottom:6px}
.banner{border:1px solid #34505a;border-radius:12px;padding:12px 18px;background:linear-gradient(110deg,#18332f,#14232e);margin-bottom:18px}
.banner b{color:#a6edda}.banner span{color:#acc0c8;font-size:13px}.stButton button{border-radius:8px}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="brand">3DE / PROJETO MECÂNICO</div>', unsafe_allow_html=True)
st.title('3DE · Oficina de criação')
st.caption('Esboce, defina as cotas e reconstrua um sólido. Projeto em milímetros.')

sketch = components.declare_component('cad_vision_sketch', path=str(Path(__file__).parent/'sketch'))

@st.cache_data(show_spinner=False, max_entries=12)
def compile_project(serialized):
    features = loads(serialized)
    if not any(f['enabled'] for f in features):
        return dict(mesh=None, history=[dict(name=f['name'], status='suprimida') for f in features],
                    volume=0, size=[0,0,0], step=None, stl=None)
    model, history = build(features)
    box = model.val().BoundingBox()
    return dict(mesh=mesh(model), history=history, volume=model.val().Volume(),
                size=[box.xlen,box.ylen,box.zlen], step=export_model(model,'STEP'), stl=export_model(model,'STL'))

for k,v in dict(features=validate(copy.deepcopy(EXAMPLE)), revision=0, selected=-1, draft=None,
                undo=[], redo=[], sketch_nonce=None, notice=None).items():
    st.session_state.setdefault(k,v)
s = st.session_state

def select(index):
    s.selected=index
    s.draft=None
    s.revision+=1

def commit(candidate, selected=None):
    candidate=validate(candidate)
    compile_project(dumps(candidate))  # Commit only after a successful complete rebuild.
    s.undo=(s.undo+[copy.deepcopy(s.features)])[-25:]
    s.redo=[]
    s.features=candidate
    select(len(candidate)-1 if selected is None else selected)
    s.notice='Peça reconstruída. Histórico atualizado.'

def restore(source, dest):
    if s[source]:
        s[dest]=(s[dest]+[copy.deepcopy(s.features)])[-25:]
        s.features=s[source].pop()
        select(-1)

with st.sidebar:
    st.markdown('### Seu projeto')
    a,b=st.columns(2)
    a.button('Desfazer', disabled=not s.undo, on_click=restore,args=('undo','redo'), width='stretch')
    b.button('Refazer', disabled=not s.redo, on_click=restore,args=('redo','undo'), width='stretch')
    st.button('＋ Nova operação', on_click=select,args=(-1,),width='stretch',type='primary')
    with st.expander('Arquivo e exemplos'):
        if st.button('Nova peça vazia'):
            commit([], -1);st.rerun()
        if st.button('Abrir peça de exemplo'):
            commit(copy.deepcopy(EXAMPLE), -1);st.rerun()
        if st.button('Exemplo com relações'):
            base=copy.deepcopy(EXAMPLE[0])
            base.update(profile='polygon', points=[[-40,-25],[40,-25],[40,25],[-40,25]],
                        constraints=[dict(type='fixed',a=0,x=-40,y=-25),
                                     dict(type='horizontal',a=0),dict(type='vertical',a=1),
                                     dict(type='horizontal',a=2),dict(type='vertical',a=3),
                                     dict(type='length',a=0,value=80),dict(type='length',a=1,value=50)])
            commit([base],0);st.rerun()
        upload=st.file_uploader('Abrir projeto JSON',type=['json'])
        if st.button('Importar projeto',disabled=upload is None):
            try:
                commit(loads(upload.getvalue()),-1);st.rerun()
            except (ValueError,RuntimeError) as exc: st.error(str(exc))
    st.divider()
    st.markdown('### Histórico da peça')
    if not s.features:st.caption('Sem operações. Crie o primeiro esboço.')
    for i,f in enumerate(s.features):
        sign={'add':'＋','cut':'−','fillet':'◖','chamfer':'⌁'}[f['operation']]
        state='' if f['enabled'] else ' · suprimida'
        st.button(f"{i+1:02}  {sign} {f['name']}{state}",key=f'tree_{i}',
                  on_click=select,args=(i,),type='primary' if i==s.selected else 'secondary',width='stretch')
    st.caption('Cada operação contém um esboço. Alterar uma cota reconstrói as operações seguintes.')

features=s.features
idx=s.selected if 0<=s.selected<len(features) else None
if s.draft is None:
    s.draft=copy.deepcopy(features[idx] if idx is not None else dict(
        name=f'Operação {len(features)+1}',operation='cut' if features else 'add',profile='rectangle',
        x=0,y=0,z=0,length=30,width=20,diameter=12,depth=10,enabled=True,plane='XY',direction=-1 if features else 1,
        extent='blind',placement='max' if features else 'absolute',points=[[-20,-15],[20,-15],[20,15],[-20,15]]))
d=s.draft
for field, default in dict(profile='rectangle', x=0., y=0., z=0., length=30., width=20.,
                           diameter=12., depth=10., plane='XY', direction=1,
                           extent='blind', placement='absolute', points=[[-20,-15],[20,-15],[20,15],[-20,15]]).items():
    d.setdefault(field, copy.deepcopy(default))
key=f'{s.revision}_{idx}'
if s.notice:
    st.success(s.notice);s.notice=None
st.markdown('<div class="banner"><b>01 Esboço</b><span> → escolha o plano e o contorno</span>　 <b>02 Operação</b><span> → adicione ou remova material</span>　 <b>03 Revisão</b><span> → edite o histórico e exporte</span></div>',unsafe_allow_html=True)
inspector, workspace=st.columns([1,2.15],gap='large')
with inspector:
    st.subheader('Nova operação' if idx is None else f'Editar · {features[idx]["name"]}')
    name=st.text_input('Nome da operação',d['name'],max_chars=80,key=f'name_{key}')
    kinds={'Adicionar':'add','Remover':'cut','Filete':'fillet','Chanfro':'chamfer'}
    operation=st.selectbox('Operação',list(kinds),index=list(kinds.values()).index(d['operation']),key=f'op_{key}')
    if operation in ('Filete','Chanfro'):
        st.caption('Modifique as arestas do sólido reconstruído até este ponto do histórico.')
        edge_labels={'Todas as arestas':'all','Arestas verticais (Z)':'vertical',
                     'Arestas paralelas a X':'horizontal_x','Arestas paralelas a Y':'horizontal_y',
                     'Arestas da face superior':'top','Arestas da face inferior':'bottom'}
        edge_values=list(edge_labels.values())
        edge_label=st.selectbox('Selecionar arestas',list(edge_labels),
            index=edge_values.index(d.get('edges','all')),key=f'edges_{key}')
        radius=st.number_input('Raio (mm)' if operation=='Filete' else 'Distância (mm)',
            min_value=.1,max_value=10000.,value=float(d.get('radius',2.)),step=.1,key=f'radius_{key}')
        enabled=st.checkbox('Operação ativa',value=d['enabled'],key=f'enabled_{key}')
        candidate_feature=dict(name=name.strip(),operation=kinds[operation],
                               radius=radius,edges=edge_labels[edge_label],enabled=enabled)
    else:
        profiles={'Retângulo':'rectangle','Círculo':'circle','Contorno por linhas':'polygon'}
        profile_label=st.selectbox('Perfil do esboço',list(profiles),index=list(profiles.values()).index(d['profile']),key=f'profile_{key}')
        profile=profiles[profile_label]
        planes=['XY','XZ','YZ']
        plane=st.selectbox('Plano de referência',planes,index=planes.index(d.get('plane','XY')),key=f'plane_{key}')
        axes={'XY':'U = X · V = Y · normal = +Z','XZ':'U = X · V = Z · normal = −Y','YZ':'U = Y · V = Z · normal = +X'}
        st.caption(axes[plane])
        placements={'Origem do projeto':'absolute','Limite + do sólido':'max','Limite − do sólido':'min'}
        placement_label=st.selectbox('Posicionar esboço em',list(placements),index=list(placements.values()).index(d.get('placement','absolute')),key=f'place_{key}')
        z=st.number_input('Deslocamento na normal (mm)',-10000.,10000.,float(d['z']),key=f'z_{key}')
        st.caption('Os limites acompanham a caixa do sólido anterior ao reconstruir. O deslocamento é relativo à referência escolhida.')
        st.markdown('**Cotas do esboço**')
        a,b=st.columns(2)
        x=a.number_input('Centro U (mm)',-10000.,10000.,float(d['x']),key=f'x_{key}')
        y=b.number_input('Centro V (mm)',-10000.,10000.,float(d['y']),key=f'y_{key}')
        length,width,diameter=d['length'],d['width'],d['diameter']
        points=d.get('points',[[-20,-15],[20,-15],[20,15],[-20,15]])
        if profile=='rectangle':
            length=a.number_input('Comprimento U (mm)',.1,10000.,float(length),key=f'length_{key}')
            width=b.number_input('Largura V (mm)',.1,10000.,float(width),key=f'width_{key}')
        elif profile=='circle':
            diameter=st.number_input('Diâmetro (mm)',.1,10000.,float(diameter),key=f'diameter_{key}')
        else:
            st.caption('Vértices relativos ao centro U/V. As relações têm prioridade sobre as coordenadas iniciais. O último ponto se liga ao primeiro.')
            table=st.data_editor(pd.DataFrame(points,columns=['U','V']),num_rows='dynamic',hide_index=True,key=f'points_{key}',
                                 column_config={c:st.column_config.NumberColumn(c,required=True,min_value=-10000,max_value=10000,format='%.3f') for c in ['U','V']})
            points=table[['U','V']].values.tolist()
        relations=copy.deepcopy(d.get('constraints',[])) if profile=='polygon' else []
        if relations:
            with st.expander(f'Relações do esboço · {len(relations)}',expanded=True):
                relation_names=dict(fixed='Fixo',horizontal='Horizontal',vertical='Vertical',length='Comprimento',
                                    parallel='Paralelos',perpendicular='Perpendiculares',equal='Iguais',dx='Distância U',dy='Distância V')
                for ri,c in enumerate(relations):
                    label=f"{ri+1}. {relation_names[c['type']]} · {'vértice' if c['type']=='fixed' else 'segmento'} {c['a']+1}"
                    if 'value' in c:
                        c['value']=st.number_input(label, min_value=.1 if c['type']=='length' else -10000.,
                            max_value=10000.,value=float(c['value']),key=f'relation_{key}_{ri}')
                    else:st.caption(label)
                st.caption('Selecione elementos na aba Esboço 2D para adicionar ou remover relações.')
        extents={'Profundidade definida':'blind','Simétrica ao esboço':'symmetric'}
        if operation=='Remover':extents['Atravessar tudo']='through'
        extent_values=list(extents.values())
        extent=extents[st.selectbox('Condição de profundidade',list(extents),index=extent_values.index(d.get('extent','blind')) if d.get('extent','blind') in extent_values else 0,key=f'extent_{key}_{operation}')]
        depth=st.number_input('Profundidade total (mm)',.1,10000.,float(d['depth']),disabled=extent=='through',key=f'depth_{key}')
        direction_label=st.radio('Sentido',['Normal +','Normal −'],index=0 if d.get('direction',1)==1 else 1,horizontal=True,disabled=extent=='symmetric',key=f'direction_{key}')
        enabled=st.checkbox('Operação ativa',value=d['enabled'],key=f'enabled_{key}')
        candidate_feature=dict(name=name.strip(),operation='add' if operation=='Adicionar' else 'cut',profile=profile,
            plane=plane,placement=placements[placement_label],x=x,y=y,z=z,length=length,width=width,diameter=diameter,
            depth=depth,direction=1 if direction_label=='Normal +' else -1,extent=extent,enabled=enabled)
        if profile=='polygon':
            candidate_feature.update(points=points,constraints=relations)
            if relations:
                try:
                    solved,_,report=solve_points(points,relations)
                    candidate_feature['points']=solved
                    st.caption('Esboço totalmente definido.' if report['freedom']==0 else f"Esboço com {report['freedom']} graus de liberdade.")
                except ConstraintError as exc:st.error(str(exc))
    s.draft=copy.deepcopy(candidate_feature)
    if st.button('Aplicar operação',type='primary',width='stretch'):
        candidate=copy.deepcopy(features)
        if idx is None:candidate.append(candidate_feature)
        else:candidate[idx]=candidate_feature
        try:
            with st.spinner('Reconstruindo e verificando o sólido…'):commit(candidate,idx if idx is not None else len(candidate)-1)
            st.rerun()
        except (ValueError,RuntimeError) as exc:st.error(str(exc))
    st.caption('Aplicar operação reconstrói a peça e atualiza o histórico.')
    if idx is not None:
        with st.expander('Organizar histórico'):
            a,b=st.columns(2)
            if a.button('Subir',disabled=idx==0):
                candidate=copy.deepcopy(features);candidate[idx-1],candidate[idx]=candidate[idx],candidate[idx-1]
                try:commit(candidate,idx-1);st.rerun()
                except (ValueError,RuntimeError) as exc:st.error(str(exc))
            if b.button('Descer',disabled=idx==len(features)-1):
                candidate=copy.deepcopy(features);candidate[idx+1],candidate[idx]=candidate[idx],candidate[idx+1]
                try:commit(candidate,idx+1);st.rerun()
                except (ValueError,RuntimeError) as exc:st.error(str(exc))
            if st.button('Excluir operação selecionada'):
                try:commit(features[:idx]+features[idx+1:],-1);st.rerun()
                except (ValueError,RuntimeError) as exc:st.error(str(exc))
with workspace:
    model_tab,sketch_tab=st.tabs(['Peça 3D','Esboço 2D'])
    with model_tab:
        try:
            result=compile_project(dumps(features))
            if result['mesh']:
                components.html(html(result['mesh']),height=535,scrolling=False)
            else:
                st.info('Peça vazia. Desenhe um perfil em Esboço 2D e aplique uma operação de adição.')
            a,b,c=st.columns(3)
            a.metric('Volume',f"{result['volume']:,.2f} mm³")
            b.metric('Dimensões X × Y × Z',' × '.join(f'{v:.1f}' for v in result['size'])+' mm')
            c.metric('Operações ativas',str(sum(f['enabled'] for f in features)))
            with st.expander('Ver reconstrução por operação'):
                st.dataframe(result['history'],hide_index=True,width='stretch')
            a,b,c=st.columns(3)
            a.download_button('Salvar projeto',dumps(features),'projeto.json','application/json',width='stretch')
            b.download_button('Exportar STEP',result['step'] or b'','peca.step','application/octet-stream',disabled=result['step'] is None,width='stretch')
            c.download_button('Exportar STL',result['stl'] or b'','peca.stl','application/octet-stream',disabled=result['stl'] is None,width='stretch')
        except (ValueError,RuntimeError) as exc:st.error(str(exc))
    with sketch_tab:
        if operation in ('Filete','Chanfro'):
            st.info('Esta operação atua nas arestas do sólido. Escolha as arestas e o tamanho no painel à esquerda.')
        else:
            st.caption('Desenhe no plano escolhido. Use o botão abaixo do desenho para enviar o perfil ao painel de cotas.')
            version=hashlib.sha256(repr(candidate_feature).encode()).hexdigest()
            value=sketch(feature=candidate_feature,version=version,key=f'sketch_{s.revision}_{idx}',default=None)
            if isinstance(value,dict) and value.get('nonce')!=s.sketch_nonce:
                s.sketch_nonce=value.get('nonce')
                if value.get('profile')==profile:
                    for field in ('x','y','length','width','diameter','points','constraints'):
                        if field in value:s.draft[field]=value[field]
                    s.revision+=1
                    st.rerun()
            st.caption('Contorno: desenhe linhas e feche no primeiro vértice. Selecione segmentos ou vértices para cotar e relacionar; Ctrl seleciona dois. Verde indica totalmente definido. O botão Usar este esboço preserva as relações no projeto.')
    with st.expander('Como trabalhar'):
        st.write('1. Escolha uma operação no histórico ou crie uma nova. 2. Para adição e corte, defina o plano, o esboço e a profundidade. Para filete e chanfro, selecione um grupo de arestas e informe o tamanho. 3. Aplique a operação. Um erro mantém a última peça válida. Desfazer/Refazer atua nas alterações aplicadas, durante esta sessão.')
        st.caption('Versão em desenvolvimento: um sólido conectado, perfis fechados e relações entre linhas. Filete e chanfro selecionam grupos de arestas, ainda sem seleção individual no visualizador. Montagens, simulação e importação SLDPRT não estão disponíveis. Salve o JSON antes de sair; STEP exporta a geometria e STL a malha em mm.')

