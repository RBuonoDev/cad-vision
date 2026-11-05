/* Original sketch interaction and Streamlit bridge. */
'use strict';
const send=(type,data={})=>window.parent.postMessage({isStreamlitMessage:true,type,...data},'*');
const cv=document.querySelector('canvas'),ctx=cv.getContext('2d'),$=id=>document.getElementById(id);
let f=null,version=null,scale=3,cx=0,cy=0,points=[],cs=[],closed=false,start=null,drag=-1,pan=null,dirty=false,fitPending=true;
let selected=[],vertices=[],mode='select',undos=[],redos=[],beforeDrag=null,freedom=null,lastList='';
const clone=o=>JSON.parse(JSON.stringify(o)),bounds=()=>cv.getBoundingClientRect();
const state=()=>clone({f,points,cs,closed});
function restore(s){f=s.f;points=s.points;cs=s.cs;closed=s.closed;selected=[];vertices=[];updateFreedom();dirty=true;draw()}
function remember(s=state()){undos.push(s);if(undos.length>40)undos.shift();redos=[]}
function message(text=''){$('error').textContent=text;send('streamlit:setFrameHeight',{height:document.body.scrollHeight})}
function updateFreedom(){if(!closed){freedom=null;return}const solved=cs.length?SketchSolver.solve(points,cs):{ok:true,freedom:points.length*2};freedom=solved.ok?solved.freedom:null}
function screen(p){return [cv.clientWidth/2+(p[0]-cx)*scale,cv.clientHeight/2-(p[1]-cy)*scale]}
function world(e,snap=true){const r=bounds();let u=cx+(e.clientX-r.left-cv.clientWidth/2)/scale,v=cy-(e.clientY-r.top-cv.clientHeight/2)/scale;const step=Math.max(.1,Number($('step').value)||5);if(snap&&$('snap').checked){u=Math.round(u/step)*step;v=Math.round(v/step)*step}return [Math.max(-10000,Math.min(10000,u)),Math.max(-10000,Math.min(10000,v))]}
function fit(){if(!f||cv.clientWidth<10){fitPending=true;return}fitPending=false;let w=f.profile==='circle'?f.diameter:f.length,h=f.profile==='circle'?f.diameter:f.width;cx=f.x;cy=f.y;if(f.profile==='polygon'&&points.length){const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);w=Math.max(...xs)-Math.min(...xs);h=Math.max(...ys)-Math.min(...ys);cx=(Math.max(...xs)+Math.min(...xs))/2;cy=(Math.max(...ys)+Math.min(...ys))/2}scale=Math.max(.01,Math.min(cv.clientWidth/(w*1.5+30),cv.clientHeight/(h*1.5+30)));draw()}
function addRelation(c){
 if(!closed)return message('Feche o contorno antes de adicionar relações.');
 if(points.length>40||cs.length>=60)return message('Limite: 40 vértices e 60 relações.');
 if(cs.some(q=>JSON.stringify(q)===JSON.stringify(c)))return message('Esta relação já existe.');
 const solved=SketchSolver.solve(points,[...cs,c]);if(!solved.ok)return message(solved.message);
 remember();points=solved.points;cs.push(c);freedom=solved.freedom;dirty=true;message();draw();
}
const names={horizontal:'Horizontal',vertical:'Vertical',length:'Comprimento',fixed:'Vértice fixo',parallel:'Paralelos',perpendicular:'Perpendiculares',equal:'Comprimentos iguais',dx:'Distância U',dy:'Distância V'};
function relationList(){const signature=JSON.stringify(cs);if(signature===lastList)return;lastList=signature;$('list').replaceChildren();
 cs.forEach((c,i)=>{const row=document.createElement('div');row.className='relation';let text=document.createElement('span');text.textContent=`${names[c.type]} · ${c.type==='fixed'?'V':'S'}${c.a+1}${c.b!==undefined?' ↔ '+(c.b+1):''}`;row.append(text);
 if(c.value!==undefined){let input=document.createElement('input');input.type='number';input.value=c.value.toFixed(3);input.step='.1';input.setAttribute('aria-label',`Valor da relação ${i+1}`);input.onchange=()=>{let value=Number(input.value);if(!Number.isFinite(value)||Math.abs(value)>10000||(c.type==='length'&&value<.1)){message('Valor de cota inválido.');input.value=c.value;return}let next=clone(cs);next[i].value=value;const solved=SketchSolver.solve(points,next);if(!solved.ok){message(solved.message);input.value=c.value;return}remember();cs=next;points=solved.points;freedom=solved.freedom;dirty=true;message();draw()};row.append(input)}
 let remove=document.createElement('button');remove.textContent='Remover';remove.setAttribute('aria-label',`Remover relação ${i+1}`);remove.onclick=()=>{remember();cs.splice(i,1);updateFreedom();dirty=true;message();draw()};row.append(remove);$('list').append(row)});
}
function draw(){if(!f)return;if(fitPending){if(cv.clientWidth>0)fit();return}const dpr=Math.min(devicePixelRatio||1,2),w=cv.clientWidth,h=cv.clientHeight;if(cv.width!==w*dpr||cv.height!==h*dpr){cv.width=w*dpr;cv.height=h*dpr}ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
 let step=Math.max(.1,Number($('step').value)||5);while(step*scale<16)step*=2;const lo=world({clientX:bounds().left,clientY:bounds().bottom},false),hi=world({clientX:bounds().right,clientY:bounds().top},false);ctx.lineWidth=1;ctx.strokeStyle='#1b303b';ctx.beginPath();for(let x=Math.ceil(lo[0]/step)*step;x<=hi[0];x+=step){let p=screen([x,0]);ctx.moveTo(p[0],0);ctx.lineTo(p[0],h)}for(let y=Math.ceil(lo[1]/step)*step;y<=hi[1];y+=step){let p=screen([0,y]);ctx.moveTo(0,p[1]);ctx.lineTo(w,p[1])}ctx.stroke();let origin=screen([0,0]);ctx.strokeStyle='#52717c';ctx.setLineDash([5,5]);ctx.beginPath();ctx.moveTo(origin[0],0);ctx.lineTo(origin[0],h);ctx.moveTo(0,origin[1]);ctx.lineTo(w,origin[1]);ctx.stroke();ctx.setLineDash([]);
 const color=freedom===0?'#74dfb0':'#70bded';ctx.beginPath();if(f.profile==='rectangle'){let p=screen([f.x-f.length/2,f.y+f.width/2]);ctx.rect(p[0],p[1],f.length*scale,f.width*scale)}else if(f.profile==='circle'){let p=screen([f.x,f.y]);ctx.arc(p[0],p[1],f.diameter*scale/2,0,2*Math.PI)}else if(points.length){points.forEach((p,i)=>{const q=screen(p);i?ctx.lineTo(...q):ctx.moveTo(...q)});if(closed)ctx.closePath()}
 ctx.strokeStyle=f.profile==='polygon'?color:'#65d8ba';ctx.fillStyle='#65d8ba18';ctx.lineWidth=2;if(f.profile!=='polygon'||closed)ctx.fill();ctx.stroke();
 if(f.profile==='polygon'){
 for(let i=0;i<(closed?points.length:points.length-1);i++){
 const a=screen(points[i]),b=screen(points[(i+1)%points.length]);if(selected.includes(i)){ctx.strokeStyle='#f2c97c';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke()}
 ctx.font='10px system-ui';ctx.fillStyle='#9ab9c7';ctx.fillText('S'+(i+1),(a[0]+b[0])/2+5,(a[1]+b[1])/2-7);
 const labels=cs.filter(c=>c.a===i&&['horizontal','vertical','length'].includes(c.type)).map(c=>c.type==='length'?c.value.toFixed(2)+' mm':c.type==='horizontal'?'H':'V');if(labels.length){ctx.fillStyle='#80e1c3';ctx.fillText(labels.join(' · '),(a[0]+b[0])/2+5,(a[1]+b[1])/2+8)}}
 points.forEach((p,i)=>{let q=screen(p);ctx.beginPath();ctx.arc(...q,vertices.includes(i)?6:3.5,0,Math.PI*2);ctx.fillStyle=cs.some(c=>c.type==='fixed'&&c.a===i)?'#f4a5b6':vertices.includes(i)?'#f2c97c':color;ctx.fill();ctx.fillStyle='#afc4cc';ctx.font='10px system-ui';ctx.fillText('V'+(i+1),q[0]+8,q[1]-8)})}
 ctx.fillStyle='#9fb5bd';ctx.font='12px system-ui';ctx.fillText('U →',w-40,h-12);ctx.fillText('V ↑',12,20);
 $('summary').textContent=f.profile==='polygon'?`${points.length} vértices · ${closed?'fechado':'aberto'}${closed&&freedom!==null?' · '+(freedom===0?'Totalmente definido':freedom+' graus de liberdade'):''}`:f.profile==='circle'?`Ø ${f.diameter.toFixed(2)} mm`:`${f.length.toFixed(2)} × ${f.width.toFixed(2)} mm`;
 $('hint').textContent=(dirty?'Alteração ainda não enviada. ':'')+(f.profile==='polygon'?(mode==='draw'&&!closed?'Clique para criar linhas; clique no primeiro vértice para fechar. ':'Clique no segmento ou vértice para selecionar; Ctrl seleciona dois. Arraste vértices para editar. '):'Arraste para desenhar. ')+'Roda: zoom · botão direito: mover · Esc: cancelar seleção.';
 $('relations').hidden=f.profile!=='polygon';$('selected').textContent=vertices.length?'Vértices: '+vertices.map(i=>i+1).join(', '):'Segmentos: '+(selected.map(i=>i+1).join(', ')||'nenhum');
 $('back').disabled=f.profile!=='polygon'||!points.length;$('apply').disabled=f.profile==='polygon'&&(!closed||points.length<3);$('undo').disabled=!undos.length;$('redo').disabled=!redos.length;
 $('select').disabled=f.profile!=='polygon';$('draw').disabled=f.profile!=='polygon';$('select').setAttribute('aria-pressed',String(mode==='select'));$('draw').setAttribute('aria-pressed',String(mode==='draw'));
 $('fix').disabled=vertices.length!==1||!closed;
 document.querySelectorAll('[data-kind]').forEach(b=>b.disabled=!closed||(b.dataset.kind==='dx'||b.dataset.kind==='dy'?vertices.length!==2:['parallel','perpendicular','equal'].includes(b.dataset.kind)?selected.length!==2:selected.length!==1));
 if(selected.length===1&&document.activeElement!==$('length')){const a=points[selected[0]],b=points[(selected[0]+1)%points.length];$('length').value=Math.hypot(b[0]-a[0],b[1]-a[1]).toFixed(3)}relationList();send('streamlit:setFrameHeight',{height:document.body.scrollHeight});
}
function nearestVertex(e){const r=bounds(),p=[e.clientX-r.left,e.clientY-r.top];return points.findIndex(q=>{q=screen(q);return Math.hypot(q[0]-p[0],q[1]-p[1])<9})}
function nearestEdge(e){const r=bounds(),p=[e.clientX-r.left,e.clientY-r.top];let best=-1,distance=9;for(let i=0;i<(closed?points.length:points.length-1);i++){const a=screen(points[i]),b=screen(points[(i+1)%points.length]),v=[b[0]-a[0],b[1]-a[1]],t=Math.max(0,Math.min(1,((p[0]-a[0])*v[0]+(p[1]-a[1])*v[1])/(v[0]**2+v[1]**2||1)));let d=Math.hypot(p[0]-a[0]-t*v[0],p[1]-a[1]-t*v[1]);if(d<distance){distance=d;best=i}}return best}
function inferred(a,b,i){if(!$('auto').checked)return;if(Math.abs(a[1]-b[1])<1e-8)cs.push({type:'horizontal',a:i});else if(Math.abs(a[0]-b[0])<1e-8)cs.push({type:'vertical',a:i})}
cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('pointerdown',e=>{
 if(!f)return;cv.setPointerCapture(e.pointerId);cv.focus();if(e.button===2||e.button===1){pan={x:e.clientX,y:e.clientY,cx,cy};return}message();beforeDrag=state();const p=world(e);if(f.profile!=='polygon'){start=p;return}
 const hit=nearestVertex(e);
 if(mode==='draw'&&!closed){remember();if(hit===0&&points.length>=3){closed=true;inferred(points.at(-1),points[0],points.length-1);mode='select';updateFreedom()}
 else if(points.length<40){if(points.length&&(e.shiftKey||$('auto').checked)){const q=points.at(-1),dx=Math.abs(p[0]-q[0]),dy=Math.abs(p[1]-q[1]);if(e.shiftKey||Math.min(dx,dy)*scale<7){if(dx>dy)p[1]=q[1];else p[0]=q[0]}}if(points.length)inferred(points.at(-1),p,points.length-1);points.push(p)}else message('Limite de 40 vértices no editor com relações.');dirty=true;draw();return}
 if(hit>=0){vertices=e.ctrlKey?[...vertices.filter(i=>i!==hit),...(vertices.includes(hit)?[]:[hit])].slice(-2):[hit];selected=[];drag=e.ctrlKey?-1:hit;draw();return}
 const edge=nearestEdge(e);vertices=[];selected=edge<0?[]:e.ctrlKey?[...selected.filter(i=>i!==edge),...(selected.includes(edge)?[]:[edge])].slice(-2):[edge];draw();
});
cv.addEventListener('pointermove',e=>{if(pan){cx=pan.cx-(e.clientX-pan.x)/scale;cy=pan.cy+(e.clientY-pan.y)/scale;draw();return}
 if(drag>=0){const p=world(e);let candidate=clone(points);candidate[drag]=p;if(cs.length){const solved=SketchSolver.solve(candidate,[...cs,{type:'fixed',a:drag,x:p[0],y:p[1]}]);if(!solved.ok){message('O movimento viola uma relação existente. Remova ou edite a relação para mover.');return}candidate=solved.points}points=candidate;dirty=true;updateFreedom();draw()}
 if(start){const p=world(e);if(f.profile==='rectangle'){f.x=(start[0]+p[0])/2;f.y=(start[1]+p[1])/2;f.length=Math.max(.1,Math.abs(start[0]-p[0]));f.width=Math.max(.1,Math.abs(start[1]-p[1]))}else{f.x=start[0];f.y=start[1];f.diameter=Math.max(.1,2*Math.hypot(p[0]-start[0],p[1]-start[1]))}dirty=true;draw()}
});
function release(){if((drag>=0||start)&&beforeDrag&&JSON.stringify(beforeDrag)!==JSON.stringify(state()))remember(beforeDrag);start=null;drag=-1;pan=null;beforeDrag=null;draw()}
cv.addEventListener('pointerup',release);cv.addEventListener('pointercancel',release);
cv.addEventListener('wheel',e=>{e.preventDefault();scale=Math.max(.01,Math.min(100,scale*Math.exp(-e.deltaY*.001)));draw()},{passive:false});
cv.addEventListener('keydown',e=>{if(e.key==='Escape'){selected=[];vertices=[];drag=-1;start=null;message();draw()}if(e.ctrlKey&&e.key==='z'){e.preventDefault();$('undo').click()}});
$('select').onclick=()=>{mode='select';draw()};$('draw').onclick=()=>{mode='draw';if(closed)message('O contorno está fechado. Use Limpar para começar outro.');draw()};
$('fit').onclick=fit;$('clear').onclick=()=>{remember();if(f.profile==='polygon'){points=[];cs=[];closed=false;mode='draw';freedom=null;selected=[];vertices=[]}else{f.x=0;f.y=0;f.length=20;f.width=20;f.diameter=20}dirty=true;message();draw()};
$('back').onclick=()=>{remember();points.pop();cs=[];closed=false;mode='draw';selected=[];vertices=[];freedom=null;dirty=true;message('Ao remover um vértice, as relações foram limpas.');draw()};$('step').onchange=draw;
$('undo').onclick=()=>{if(!undos.length)return;redos.push(state());restore(undos.pop());message()};$('redo').onclick=()=>{if(!redos.length)return;undos.push(state());restore(redos.pop());message()};
$('fix').onclick=()=>{const i=vertices[0];if(i!==undefined)addRelation({type:'fixed',a:i,x:points[i][0],y:points[i][1]})};
for(const b of document.querySelectorAll('[data-kind]'))b.onclick=()=>{const t=b.dataset.kind,verts=t==='dx'||t==='dy',c={type:t,a:(verts?vertices:selected)[0]};if(['parallel','perpendicular','equal','dx','dy'].includes(t))c.b=(verts?vertices:selected)[1];if(t==='length'||verts){c.value=Number($(verts?'distance':'length').value);if(!Number.isFinite(c.value)||Math.abs(c.value)>10000||(t==='length'&&c.value<.1))return message('Cota inválida.')}addRelation(c)};
$('apply').onclick=()=>{
 if(f.profile==='polygon'&&cs.length){const solved=SketchSolver.solve(points,cs);if(!solved.ok)return message(solved.message);points=solved.points}
 let value={profile:f.profile,x:f.x,y:f.y,length:f.length,width:f.width,diameter:f.diameter,nonce:Date.now()};if(f.profile==='polygon'){value.x=0;value.y=0;value.points=clone(points);value.constraints=clone(cs)}send('streamlit:setComponentValue',{value,dataType:'json'});dirty=false;draw();$('hint').textContent='Esboço enviado. Clique em Aplicar operação para reconstruir a peça.';
};
window.addEventListener('message',e=>{if(e.source!==window.parent||e.data?.type!=='streamlit:render')return;const a=e.data.args;if(a.version!==version){version=a.version;f=clone(a.feature);points=(f.points||[]).map(p=>[p[0]+f.x,p[1]+f.y]);cs=clone(f.constraints||[]).map(c=>c.type==='fixed'?{...c,x:c.x+f.x,y:c.y+f.y}:c);closed=points.length>=3;mode=closed?'select':'draw';dirty=false;selected=[];vertices=[];undos=[];redos=[];message();$('plane').textContent=`PLANO ${f.plane} · mm`;updateFreedom();fit()}draw()});
new ResizeObserver(()=>{draw();send('streamlit:setFrameHeight',{height:document.body.scrollHeight})}).observe(cv);send('streamlit:componentReady',{apiVersion:1});send('streamlit:setFrameHeight',{height:730});
