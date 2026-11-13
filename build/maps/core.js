const N=1400;
function closedSpline(ctrl){
  const n=ctrl.length,dense=[],al=.5;
  for(let i=0;i<n;i++){
    const P=[ctrl[(i+n-1)%n],ctrl[i],ctrl[(i+1)%n],ctrl[(i+2)%n]];
    const t=[0];for(let k=1;k<4;k++)t.push(t[k-1]+Math.pow(Math.hypot(P[k][0]-P[k-1][0],P[k][1]-P[k-1][1])||1,al));
    const M=24;
    for(let s=0;s<M;s++){
      const u=t[1]+(t[2]-t[1])*s/M,q=[0,0];
      for(let a=0;a<2;a++){
        const A1=(t[1]-u)/(t[1]-t[0])*P[0][a]+(u-t[0])/(t[1]-t[0])*P[1][a];
        const A2=(t[2]-u)/(t[2]-t[1])*P[1][a]+(u-t[1])/(t[2]-t[1])*P[2][a];
        const A3=(t[3]-u)/(t[3]-t[2])*P[2][a]+(u-t[2])/(t[3]-t[2])*P[3][a];
        const B1=(t[2]-u)/(t[2]-t[0])*A1+(u-t[0])/(t[2]-t[0])*A2;
        const B2=(t[3]-u)/(t[3]-t[1])*A2+(u-t[1])/(t[3]-t[1])*A3;
        q[a]=(t[2]-u)/(t[2]-t[1])*B1+(u-t[1])/(t[2]-t[1])*B2;
      }
      dense.push(q);
    }
  }
  const m=dense.length,cum=[0];
  for(let i=1;i<=m;i++){const a=dense[i%m],b=dense[i-1];cum.push(cum[i-1]+Math.hypot(a[0]-b[0],a[1]-b[1]))}
  const L=cum[m],out=[];let j=0;
  for(let i=0;i<N;i++){const s=i/N*L;while(cum[j+1]<s)j++;const f=(s-cum[j])/((cum[j+1]-cum[j])||1),a=dense[j],b=dense[(j+1)%m];out.push([a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f])}
  return out;
}
function seoulPts(){const P=[];for(let i=0;i<N;i++){const t=i/N*Math.PI*2+1.867;const r=1+.17*Math.sin(3*t+.6)+.11*Math.sin(5*t+2.1)+.06*Math.sin(8*t+.4);P.push([360*r*Math.cos(t),230*r*Math.sin(t)])}return P}
function mountainCtrl(){
  const X=.7,c=[];const p=(x,z)=>c.push([x*X,z]);
  p(0,0);p(85,-13);p(170,12);p(260,-12);p(350,14);p(430,0);
  p(486,16);p(522,48);p(492,86);
  p(420,98);p(335,76);p(240,104);p(150,80);p(70,96);
  p(10,104);p(-24,140);p(10,176);
  p(80,184);p(170,166);p(265,194);p(355,168);p(430,184);
  p(486,198);p(522,228);p(492,266);
  p(420,278);p(335,254);p(240,284);p(150,260);p(70,276);
  p(10,284);p(-24,320);p(10,356);
  p(85,364);p(175,346);p(265,374);p(350,352);p(430,366);
  p(520,372);p(600,330);p(640,250);p(650,150);p(630,40);p(590,-60);p(520,-118);
  p(430,-110);p(340,-136);p(250,-108);p(160,-134);p(75,-112);p(0,-118);p(-70,-100);p(-100,-50);p(-70,-8);
  return c;
}
function xmasCtrl(){
  const c=[];for(let i=0;i<20;i++){const t=i/20*Math.PI*2;const r=1+.10*Math.sin(2*t+.9)+.12*Math.sin(3*t+2.2)+.075*Math.sin(5*t+.4)+.03*Math.sin(7*t+1.3);c.push([300*r*Math.cos(t),185*r*Math.sin(t)])}return c;
}
function elev(top,drop,uc){
  const raw=[];for(let i=0;i<N;i++){const u=i/N;raw.push(u<uc?top-drop*(u/uc):top-drop+drop*((u-uc)/(1-uc)))}
  let a=raw;for(let pass=0;pass<3;pass++){const b=[];for(let i=0;i<N;i++){let s=0;for(let k=-30;k<=30;k++)s+=a[(i+k+N)%N];b.push(s/61)}a=b}
  return a;
}
if(typeof module!=='undefined')module.exports={N,closedSpline,seoulPts,mountainCtrl,xmasCtrl,elev};
