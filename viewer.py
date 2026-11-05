"""Own viewer glue using the public Three.js library."""
import json


def html(mesh):
    data = json.dumps(mesh, allow_nan=False, separators=(',', ':'))
    return '''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<style>html,body{margin:0;height:100%;overflow:hidden;background:#0b1425;color:#e0ecff;font:13px system-ui}#view{position:absolute;inset:0}#status{position:absolute;top:12px;left:12px;z-index:2;background:#17263cdd;padding:9px;border-radius:8px}</style>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<div id="view"></div><div id="status">Carregando modelo…</div><script>
const status=document.getElementById('status');
const deadline=setTimeout(()=>status.textContent='Falha no carregamento. Confira a conexão com os CDNs.',12000);
window.addEventListener('DOMContentLoaded',()=>{try{
if(!window.THREE||!THREE.OrbitControls)throw Error('Bibliotecas 3D indisponíveis');
const data=__MESH__;
const positions=[];for(const face of data.triangles)for(const i of face)positions.push(...data.vertices[i]);
const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.computeVertexNormals();geometry.computeBoundingBox();
const box=geometry.boundingBox,center=box.getCenter(new THREE.Vector3()),extent=box.getSize(new THREE.Vector3());
geometry.translate(-center.x,-center.y,-center.z);
const size=Math.max(extent.x,extent.y,extent.z),host=document.getElementById('view');
const scene=new THREE.Scene();scene.background=new THREE.Color('#0b1425');
const camera=new THREE.PerspectiveCamera(40,1,size/10000,size*100);camera.up.set(0,0,1);camera.position.set(size*1.5,-size*1.8,size*1.4);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));host.appendChild(renderer.domElement);
scene.add(new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0x3ba8ec,metalness:.25,roughness:.4})));
scene.add(new THREE.LineSegments(new THREE.EdgesGeometry(geometry,25),new THREE.LineBasicMaterial({color:0x103b57})));
scene.add(new THREE.HemisphereLight(0xffffff,0x4d6079,1.8));const light=new THREE.DirectionalLight(0xffffff,1.7);light.position.set(1,-2,4);scene.add(light);
const grid=new THREE.GridHelper(size*2.5,20,0x4f6783,0x263549);grid.rotateX(Math.PI/2);grid.position.z=-extent.z/2-.01;scene.add(grid);
const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.update();
function resize(){const w=host.clientWidth||800,h=host.clientHeight||520;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}
window.addEventListener('resize',resize);resize();
let running=true;window.addEventListener('pagehide',()=>{running=false;controls.dispose();renderer.dispose()});
function draw(){if(!running)return;requestAnimationFrame(draw);controls.update();renderer.render(scene,camera)}draw();
clearTimeout(deadline);status.textContent='Arraste para girar · Roda para zoom · Botão direito para deslocar';
}catch(e){clearTimeout(deadline);status.textContent='Não foi possível renderizar: '+e.message}});
</script></html>'''.replace('__MESH__', data)
