/* Independent numerical planar constraint solver. No vendor CAD code. */
(function(root){
'use strict';
const norm=v=>Math.hypot(...v);
function residual(flat,cs){
 const n=flat.length/2,p=i=>[flat[2*i],flat[2*i+1]],seg=i=>{const a=p(i),b=p((i+1)%n);return [b[0]-a[0],b[1]-a[1]]},out=[];
 for(const c of cs){const a=p(c.a),t=c.type;if(t==='fixed'){out.push(a[0]-c.x,a[1]-c.y);continue}
 if(t==='dx'||t==='dy'){const dim=t==='dx'?0:1;out.push(p(c.b)[dim]-a[dim]-c.value);continue}
 const u=seg(c.a);if(t==='horizontal')out.push(u[1]);else if(t==='vertical')out.push(u[0]);else if(t==='length')out.push(norm(u)-c.value);else{const v=seg(c.b);out.push(t==='equal'?norm(u)-norm(v):(t==='parallel'?u[0]*v[1]-u[1]*v[0]:u[0]*v[0]+u[1]*v[1])/Math.max(norm(u),norm(v),.1))}}
 return out;
}
function jacobian(flat,cs,r){const j=r.map(()=>Array(flat.length).fill(0));for(let k=0;k<flat.length;k++){let x=[...flat],h=1e-5;x[k]+=h;let q=residual(x,cs);for(let i=0;i<r.length;i++)j[i][k]=(q[i]-r[i])/h}return j}
function linear(A,b){A=A.map((r,i)=>[...r,b[i]]);const n=b.length;for(let i=0;i<n;i++){let pivot=i;for(let k=i+1;k<n;k++)if(Math.abs(A[k][i])>Math.abs(A[pivot][i]))pivot=k;[A[i],A[pivot]]=[A[pivot],A[i]];if(Math.abs(A[i][i])<1e-14)return null;let d=A[i][i];for(let k=i;k<=n;k++)A[i][k]/=d;for(let j=0;j<n;j++)if(j!==i){d=A[j][i];for(let k=i;k<=n;k++)A[j][k]-=d*A[i][k]}}return A.map(r=>r[n])}
function rank(A){if(!A.length)return 0;A=A.map(r=>[...r]);let row=0;for(let col=0;col<A[0].length&&row<A.length;col++){let pivot=row;for(let k=row+1;k<A.length;k++)if(Math.abs(A[k][col])>Math.abs(A[pivot][col]))pivot=k;if(Math.abs(A[pivot][col])<1e-6)continue;[A[row],A[pivot]]=[A[pivot],A[row]];let d=A[row][col];for(let k=col;k<A[0].length;k++)A[row][k]/=d;for(let j=row+1;j<A.length;j++){d=A[j][col];for(let k=col;k<A[0].length;k++)A[j][k]-=d*A[row][k]}row++}return row}
function solve(points,cs){
 if(points.length>40||cs.length>60)return {ok:false,message:'Limite: 40 vértices e 60 relações.'};
 let x=points.flat(),damping=1e-6;if(!cs.length)return {ok:true,points:points.map(p=>[...p]),freedom:x.length,error:0};
 for(let iter=0;iter<100;iter++){const r=residual(x,cs);if(Math.max(...r.map(Math.abs))<1e-7)break;const j=jacobian(x,cs,r),m=r.length;
 const A=Array.from({length:m},(_,i)=>Array.from({length:m},(_,k)=>j[i].reduce((v,q,t)=>v+q*j[k][t],0)+(i===k?damping:0)));
 const w=linear(A,r);if(!w)break;const delta=x.map((_,k)=>j.reduce((v,row,i)=>v+row[k]*w[i],0));
 let improved=false,old=r.reduce((s,v)=>s+v*v,0);
 for(const alpha of [1,.5,.1,.02]){const candidate=x.map((v,i)=>Math.max(-10000,Math.min(10000,v-alpha*delta[i]))),cost=residual(candidate,cs).reduce((s,v)=>s+v*v,0);if(cost<old){x=candidate;improved=true;damping=Math.max(1e-9,damping*.5);break}}
 if(!improved){damping*=10;if(damping>1e8)break}}
 const r=residual(x,cs),error=Math.max(...r.map(Math.abs));if(!Number.isFinite(error)||error>1e-5)return {ok:false,message:'Relações conflitantes. A geometria anterior foi preservada.'};
 return {ok:true,points:Array.from({length:points.length},(_,i)=>[x[2*i],x[2*i+1]]),freedom:x.length-rank(jacobian(x,cs,r)),error};
}
const api={solve,residual};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.SketchSolver=api;
})(typeof globalThis!=='undefined'?globalThis:this);
