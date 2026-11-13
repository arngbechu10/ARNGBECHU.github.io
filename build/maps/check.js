const m=require('./core.js');
function metrics(P,name){
  const N=P.length;let L=0;for(let i=0;i<N;i++){const a=P[i],b=P[(i+1)%N];L+=Math.hypot(a[0]-b[0],a[1]-b[1])}
  // min radius via 3-point circle over step 6
  let minR=1e9,at=0;const st=6;
  for(let i=0;i<N;i++){const a=P[(i-st+N)%N],b=P[i],c=P[(i+st)%N];
    const A=Math.hypot(b[0]-a[0],b[1]-a[1]),B=Math.hypot(c[0]-b[0],c[1]-b[1]),C=Math.hypot(c[0]-a[0],c[1]-a[1]);
    const area2=Math.abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]));const R=A*B*C/(2*area2+1e-9);if(R<minR){minR=R;at=i}}
  // min separation between non-adjacent (arc distance > 150m)
  const sp=L/N;let minD=1e9,pi=0,pj=0;
  for(let i=0;i<N;i+=2)for(let j=i+1;j<N;j+=2){const ds=Math.min(j-i,N-(j-i))*sp;if(ds<150)continue;const d=Math.hypot(P[i][0]-P[j][0],P[i][1]-P[j][1]);if(d<minD){minD=d;pi=i;pj=j}}
  console.log(name,'len',L.toFixed(0),'minR',minR.toFixed(1),'@',at,'minSep',minD.toFixed(1),pi,pj);
}
const M=m.closedSpline(m.mountainCtrl()),X=m.closedSpline(m.xmasCtrl()),S=m.seoulPts();
metrics(S,'seoul');metrics(M,'mountain');metrics(X,'xmas');
require('fs').writeFileSync('pts.json',JSON.stringify({M,X,S}));
