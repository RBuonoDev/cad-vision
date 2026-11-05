"""Original Three.js viewer with mechanical views and true solid edges."""
import json


def html(mesh):
    data=json.dumps(mesh,allow_nan=False,separators=(',',':'))
    return '''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<style>*{box-sizing:border-box}html,body{margin:0;height:100%;overflow:hidden;background:#101c26;color:#dae9ed;font:12px system-ui}#view{position:absolute;inset:0}#bar{position:absolute;top:12px;left:12px;right:12px;z-index:2;display:flex;gap:5px;flex-wrap:wrap}button{background:#18303de8;color:#d7e6eb;border:1px solid #375460;border-radius:7px;padding:7px 9px;cursor:pointer}button:hover{border-color:#65d8ba}button[aria-pressed=true]{color:#8eebd0;border-color:#58b89d}#status{position:absolute;bottom:12px;left:14px;right:14px;color:#abc3ce;pointer-events:none;background:#101c26b0;padding:6px}#badge{position:absolute;bottom:48px;right:14px;font-size:10px;letter-spacing:2px;color:#6e999d}</style>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<div id="view"></div><div id="bar"><button data-view="iso">Isométrica</button><button data-view="front">Frontal</button><button data-view="top">Superior</button><button data-view="right">Direita</button><button id="fit">Enquadrar</button><button id="edges" aria-pressed="true">Arestas</button><button id="wire" aria-pressed="false">Aramado</button><button id="grid" aria-pressed="true">Grade</button></div><div id="badge">3DE / mm</div><div id="status">Carregando modelo…</div><script>
const status=document.getElementById('status');const deadline=setTimeout(()=>status.textContent='Não foi possível carregar as bibliotecas 3D. Verifique a conexão e recarregue.',12000);
window.addEventListener('DOMContentLoaded',()=>{try{
if(!window.THREE||!THREE.OrbitControls)throw Error('Bibliotecas 3D indisponíveis');const data=__MESH__;
const positions=[];for(const face of data.triangles)for(const i of face)positions.push(...data.vertices[i]);
const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.computeVertexNormals();geometry.computeBoundingBox();
const box=geometry.boundingBox,center=box.getCenter(new THREE.Vector3()),extent=box.getSize(new THREE.Vector3());geometry.translate(-center.x,-center.y,-center.z);
const size=Math.max(extent.x,extent.y,extent.z,1),host=document.getElementById('view');const scene=new THREE.Scene();scene.background=new THREE.Color('#101c26');
const camera=new THREE.OrthographicCamera(-size,size,size,-size,.01,size*200);camera.up.set(0,0,1);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));host.appendChild(renderer.domElement);
const material=new THREE.MeshStandardMaterial({color:0x8dbdb7,metalness:.35,roughness:.4,polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1});scene.add(new THREE.Mesh(geometry,material));
let lineGeometry;
if(data.edges){let coords=[];for(const edge of data.edges)for(let i=1;i<edge.length;i++)for(const p of [edge[i-1],edge[i]])coords.push(p[0]-center.x,p[1]-center.y,p[2]-center.z);lineGeometry=new THREE.BufferGeometry();lineGeometry.setAttribute('position',new THREE.Float32BufferAttribute(coords,3))}else lineGeometry=new THREE.EdgesGeometry(geometry,25);
const edges=new THREE.LineSegments(lineGeometry,new THREE.LineBasicMaterial({color:0x203a40}));scene.add(edges);
scene.add(new THREE.HemisphereLight(0xffffff,0x38576a,1.6));const light=new THREE.DirectionalLight(0xffffff,1.6);light.position.set(1,-2,4);scene.add(light);
const grid=new THREE.GridHelper(size*3,30,0x527276,0x243b49);grid.rotateX(Math.PI/2);grid.position.z=-extent.z/2-size*.01;scene.add(grid);
const axes=new THREE.AxesHelper(size*.2);axes.position.set(-size*.8,-size*.7,-extent.z/2);scene.add(axes);
const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
function resize(){const w=host.clientWidth||800,h=host.clientHeight||535;const aspect=w/h,half=size*.78;camera.left=-half*aspect;camera.right=half*aspect;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}
function view(which){controls.target.set(0,0,0);camera.up.set(0,0,1);const dirs={iso:[1.4,-1.8,1.3],front:[0,-3,0],top:[0,0,3],right:[3,0,0]};if(which==='top')camera.up.set(0,1,0);camera.position.set(...dirs[which].map(v=>v*size));camera.zoom=1;camera.lookAt(0,0,0);camera.updateProjectionMatrix();controls.update();document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===which)))}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));document.getElementById('fit').onclick=()=>view('iso');
for(const [id,fn] of [['edges',v=>edges.visible=v],['wire',v=>material.wireframe=v],['grid',v=>grid.visible=v]])document.getElementById(id).onclick=function(){let v=this.getAttribute('aria-pressed')!=='true';this.setAttribute('aria-pressed',String(v));fn(v)};
window.addEventListener('resize',resize);resize();view('iso');let running=true;window.addEventListener('pagehide',()=>{running=false;controls.dispose();geometry.dispose();lineGeometry.dispose();renderer.dispose()});
function draw(){if(!running)return;requestAnimationFrame(draw);controls.update();renderer.render(scene,camera)}draw();clearTimeout(deadline);status.textContent='Arraste: girar · Roda: zoom · Botão direito: mover · Projeção ortográfica';
}catch(e){clearTimeout(deadline);status.textContent='Não foi possível renderizar: '+e.message}});
</script></html>'''.replace('__MESH__',data)

