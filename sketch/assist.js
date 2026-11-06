/* Independent drawing feedback and geometric snapping. */
let referenceEdges=[],referencePlane='',hoverSketch=null,snapCue=null,hoverEdge=-1;
function snapPoint(e){
 const raw=world(e,false);snapCue=null;if(e.altKey)return raw;
 if($('geometrysnap').checked){
  const candidates=[{p:[0,0],label:'Origem'},...points.map((p,i)=>({p,label:'Extremidade V'+(i+1)}))];
  for(let i=0;i<(closed?points.length:points.length-1);i++){const a=points[i],b=points[(i+1)%points.length];candidates.push({p:[(a[0]+b[0])/2,(a[1]+b[1])/2],label:'Ponto médio S'+(i+1)})}
  if($('background').checked)for(const edge of referenceEdges)if(edge.length){candidates.push({p:edge[0],label:'Vértice da peça (referência)'},{p:edge.at(-1),label:'Vértice da peça (referência)'})}
  let best=null,d=10;for(const c of candidates){const dist=Math.hypot(c.p[0]-raw[0],c.p[1]-raw[1])*scale;if(dist<d){d=dist;best=c}}
  if(best){snapCue=best;return [...best.p]}
 }
 let p=world(e);
 if(mode==='draw'&&!closed&&points.length&&($('auto').checked||e.shiftKey)){
  const last=points.at(-1),dx=Math.abs(p[0]-last[0]),dy=Math.abs(p[1]-last[1]);if(e.shiftKey||Math.min(dx,dy)*scale<8){if(dx>dy){p[1]=last[1];snapCue={p:[...p],label:'Horizontal'}}else{p[0]=last[0];snapCue={p:[...p],label:'Vertical'}}}
 }
 return p;
}
function backgroundSketch(){
 if(!$('background').checked)return;ctx.save();ctx.lineWidth=1.4;ctx.strokeStyle='#668d9b';ctx.globalAlpha=.46;ctx.setLineDash([]);ctx.beginPath();for(const edge of referenceEdges){edge.forEach((p,i)=>{const q=screen(p);i?ctx.lineTo(...q):ctx.moveTo(...q)})}ctx.stroke();ctx.restore();
}
function feedbackSketch(){
 ctx.save();
 if($('origin').checked){const o=screen([0,0]);ctx.strokeStyle='#e6a0b0';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(o[0]-6,o[1]);ctx.lineTo(o[0]+6,o[1]);ctx.moveTo(o[0],o[1]-6);ctx.lineTo(o[0],o[1]+6);ctx.stroke();ctx.fillStyle='#e6a0b0';ctx.font='11px system-ui';ctx.fillText('0',o[0]+8,o[1]+13)}
 if(hoverSketch&&mode==='draw'&&!closed&&f.profile==='polygon'&&points.length){const p=points.at(-1),a=screen(p),b=screen(hoverSketch);ctx.setLineDash([6,4]);ctx.strokeStyle='#f2c97c';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke();ctx.setLineDash([]);const len=Math.hypot(hoverSketch[0]-p[0],hoverSketch[1]-p[1]),angle=Math.atan2(hoverSketch[1]-p[1],hoverSketch[0]-p[0])*180/Math.PI;ctx.fillStyle='#f2c97c';ctx.font='12px system-ui';ctx.fillText(`${len.toFixed(2)} mm · ${angle.toFixed(1)}°`,b[0]+12,b[1]-12)}
 if(hoverEdge>=0&&!selected.includes(hoverEdge)&&mode==='select'&&f.profile==='polygon') {const a=screen(points[hoverEdge]),b=screen(points[(hoverEdge+1)%points.length]);ctx.lineWidth=3;ctx.strokeStyle='#f4a658';ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke()}
 if(snapCue&&hoverSketch){const q=screen(snapCue.p);ctx.strokeStyle='#f4a658';ctx.lineWidth=2;ctx.strokeRect(q[0]-5,q[1]-5,10,10);ctx.fillStyle='#f4a658';ctx.font='11px system-ui';ctx.fillText(snapCue.label,q[0]+11,q[1]+17);if(['Horizontal','Vertical'].includes(snapCue.label)){const a=screen(points.at(-1));ctx.setLineDash([3,4]);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...q);ctx.stroke()}}
 if(hoverSketch)$('cursorinfo').textContent=`U ${hoverSketch[0].toFixed(3)} · V ${hoverSketch[1].toFixed(3)} mm${snapCue?' · '+snapCue.label:''} · Alt ignora encaixes · L linhas · S selecionar · F enquadrar · Enter fechar contorno`;
 ctx.restore();
}
function contourIssue(ps){
 if(ps.length<3)return 'Feche um contorno com pelo menos três vértices.';
 const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
 const on=(a,b,p)=>Math.abs(cross(a,b,p))<1e-8&&p[0]>=Math.min(a[0],b[0])-1e-8&&p[0]<=Math.max(a[0],b[0])+1e-8&&p[1]>=Math.min(a[1],b[1])-1e-8&&p[1]<=Math.max(a[1],b[1])+1e-8;
 for(let i=0;i<ps.length;i++){
 const a=ps[i],b=ps[(i+1)%ps.length];if(Math.hypot(a[0]-b[0],a[1]-b[1])<.01)return 'Há segmentos muito curtos ou pontos repetidos.';
 for(let j=i+1;j<ps.length;j++){if(j===i+1||(i===0&&j===ps.length-1))continue;const c=ps[j],d=ps[(j+1)%ps.length];if((cross(a,b,c)*cross(a,b,d)<0&&cross(c,d,a)*cross(c,d,b)<0)||on(a,b,c)||on(a,b,d)||on(c,d,a)||on(c,d,b))return 'O contorno se cruza ou encosta em si mesmo.';}}
 const area=Math.abs(ps.reduce((sum,a,i)=>{const b=ps[(i+1)%ps.length];return sum+a[0]*b[1]-b[0]*a[1]},0))/2;
 return area<.01?'O contorno não tem área suficiente.':'';
}
