import re, base64, sys
W='/tmp/claude-0/-home-claude/f9ae0b19-9e15-514d-b64c-42a1ff34b6c5/scratchpad/w/'
h=open(W+'t_nitro.html',encoding='utf-8').read()
b64=lambda p,m:'data:'+m+';base64,'+base64.b64encode(open(W+'maps/'+p,'rb').read()).decode()

# ---- 1) 기존 트랙/하늘 블록 추출 ----
a=h.index("const SKY_URI='")
b=h.index("/* 헤드라이트 빛 번짐 */")
old=h[a:b]
seoul=re.search(r"const SKY_URI='([^']+)'",old).group(1)
asph=re.search(r"rep\(TL\.load\('(data:image/jpeg;base64,[^']+)'\)\)",old).group(1)

core=open(W+'maps/core.js').read().split("if(typeof module")[0]

new=r"""
/* ================= 맵 시스템 ================= */
const SKIES={seoul:'%SEOUL%',mountain:'%SKYM%',xmas:'%SKYX%'};
const skyCache={};
const skyTex=id=>skyCache[id]||(skyCache[id]=rep(TL.load(SKIES[id])));
const skyMat=new THREE.MeshBasicMaterial({map:skyTex('seoul'),side:THREE.BackSide,transparent:true,fog:false,depthWrite:false});
const sky=new THREE.Mesh(new THREE.CylinderGeometry(1000,1000,942,96,1,true),skyMat);
sky.renderOrder=-1;S.add(sky);const SKY_Y=70;
const gnd=new THREE.Mesh(new THREE.PlaneGeometry(6000,6000),new THREE.MeshBasicMaterial({color:0x0d0e1e}));
gnd.rotation.x=-Math.PI/2;S.add(gnd);

/* 코스 생성 (N=1400개 점으로 균일하게 나눈 폐곡선) */
%CORE%
const asphT=rep(TL.load('%ASPH%'));
function mkTex(w,h,fn){const cv=document.createElement('canvas');cv.width=w;cv.height=h;fn(cv.getContext('2d'),w,h);return rep(new THREE.CanvasTexture(cv))}
const sm01=t=>{t=clamp(t,0,1);return t*t*(3-2*t)};

const MAPS={
  seoul:{half:8,wall:2,rail:'jersey',bridge:true,bg:0x3b5588,fog:[0x0d0e1e,90,650],gnd:0x0d0e1e,gy:-.03,asph:0x7f879a,kerb:['#c4352b','#e9e9ee'],pts:seoulPts,lamps:{gap:45,col:'255,236,190',size:16}},
  mountain:{half:12,wall:2.5,bg:0x9db7d6,fog:[0xaec4d8,110,720],gnd:0x6f8f6a,gy:-75,asph:0xc2c5cc,kerb:['#f1f1f4','#a7adb6'],pts:()=>closedSpline(mountainCtrl()),elev:[80,80,.78],terrain:true,rail:'guard'},
  xmas:{half:14,wall:3,bg:0x16254a,fog:[0x1a2a58,70,560],gnd:0x8798c2,gy:-.03,asph:0x9aa1b8,kerb:['#c4352b','#f4f4f7'],pts:()=>closedSpline(xmasCtrl()),lamps:{gap:36,col:'255,214,150',size:15},rail:'fence',trees:true,shoulder:0xb4c2e2}
};
let BR=null,RIVER=null,WATERT=null,TP=[],TY=[],TSL=[],TS=[0],TN=[],TH=[],TLEN=0,HALF=8,WALL=0,sx=0,sz=0,sh=0,MAPID='seoul',MG=null,terrH=null;

function clearMap(){
  if(!MG)return;S.remove(MG);
  MG.traverse(o=>{if(o.geometry)o.geometry.dispose();
    if(o.material){(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{if(m.map&&m.map!==asphT)m.map.dispose();m.dispose()})}});
  MG=null;
}
function strip(o1,o2,y,uvf,mat){
  const p=[],uv=[],ix=[];
  for(let i=0;i<=N;i++){const k=i%N,n=TN[k],q=TP[k];
    p.push(q[0]+n[0]*o1,y+TY[k],q[1]+n[1]*o1,q[0]+n[0]*o2,y+TY[k],q[1]+n[1]*o2);
    uv.push(...uvf(i,0),...uvf(i,1));}
  for(let i=0;i<N;i++){const k=i*2;ix.push(k,k+1,k+2,k+1,k+3,k+2)}
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));
  g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(ix);
  const m=new THREE.Mesh(g,mat);MG.add(m);return m;
}
/* 세로 벽(바리케이드): 도로 중심에서 off만큼 떨어진 곳에 높이 h (i0~i1 구간, yoff는 시작 높이) */
function wallStrip(off,h,mat,per,i0=0,i1=N,yoff=0){
  const p=[],uv=[],ix=[];
  for(let i=i0;i<=i1;i++){const k=i%N,n=TN[k],q=TP[k],x=q[0]+n[0]*off,z=q[1]+n[1]*off;
    p.push(x,TY[k]+yoff,z,x,TY[k]+yoff+h,z);uv.push(TS[i]/per,0,TS[i]/per,1)}
  for(let i=0;i<i1-i0;i++){const k=i*2;ix.push(k,k+1,k+2,k+1,k+3,k+2)}
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));
  g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(ix);
  MG.add(new THREE.Mesh(g,mat));
}
function glowTex(r,g,b){const cv=document.createElement('canvas');cv.width=cv.height=64;const x=cv.getContext('2d');
  const gr=x.createRadialGradient(32,32,0,32,32,32);gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(.25,'rgba('+r+','+g+','+b+',.6)');gr.addColorStop(1,'rgba('+r+','+g+','+b+',0)');
  x.fillStyle=gr;x.fillRect(0,0,64,64);return new THREE.CanvasTexture(cv)}
function nearD(x,z){let bd=1e18,bi=0;for(let i=0;i<N;i+=1){const dx=x-TP[i][0],dz=z-TP[i][1],d=dx*dx+dz*dz;if(d<bd){bd=d;bi=i}}return [Math.sqrt(bd),bi]}


/* 나무: 여러 층으로 겹친 가문비나무 + 줄기. 층마다 모양을 살짝 흩트려 자연스럽게 */
function spruceGeo(opt){
  const pos=[],col=[],tiers=opt.tiers||6,H=opt.h||14,R=opt.r||3.3,tH=H*.12;
  const add=(g,colorFn)=>{g=g.toNonIndexed();const p=g.attributes.position;for(let i=0;i<p.count;i++){pos.push(p.getX(i),p.getY(i),p.getZ(i));col.push(...colorFn(p.getX(i),p.getY(i),p.getZ(i)))}};
  const trunk=new THREE.CylinderGeometry(.22,.4,tH+H*.25,6);trunk.translate(0,(tH+H*.25)/2,0);
  add(trunk,()=>[.26,.19,.13]);
  for(let t=0;t<tiers;t++){
    const f=t/tiers,r=R*(1-f*.86)*(.9+Math.random()*.2),h=(H-tH)/tiers*2.1,y0=tH*.8+f*(H-tH-h*.55);
    const g=new THREE.ConeGeometry(r,h,11,1,true);
    const p=g.attributes.position;
    for(let i=0;i<p.count;i++){const y=p.getY(i);if(y<0){const a=Math.atan2(p.getZ(i),p.getX(i)),k=1+.22*Math.sin(a*3+t*2.1)+.12*Math.sin(a*5+t);p.setX(i,p.getX(i)*k);p.setZ(i,p.getZ(i)*k);p.setY(i,y-r*.10*Math.abs(Math.sin(a*4+t)))}}
    g.translate(0,y0+h/2,0);
    const sn=opt.snow;
    add(g,(x,y,z)=>{const u=(y-y0)/h,lit=.55+.5*clamp(u,0,1);
      if(sn){const w=sm01((u-.28)/.35);return [(.10+.55*w)*lit+.35*w,(.30+.50*w)*lit+.37*w,(.20+.55*w)*lit+.42*w]}
      return [.07*lit+.03,.25*lit+.05,.10*lit+.03]});
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));return g;
}

/* 산 지형: 도로는 산비탈을 파고 지나가요. 도로에서 멀어지면 원래 산 경사로 이어져요 */
function buildTerrain(){
  const pad=320,cell=8;let x0=1e9,x1=-1e9,z0=1e9,z1=-1e9;
  TP.forEach(p=>{x0=Math.min(x0,p[0]);x1=Math.max(x1,p[0]);z0=Math.min(z0,p[1]);z1=Math.max(z1,p[1])});
  x0-=pad;x1+=pad;z0-=pad;z1+=pad;
  const gx=Math.ceil((x1-x0)/cell)+1,gz=Math.ceil((z1-z0)/cell)+1,e0=HALF+16;
  const base=(x,z)=>78-.2*z+9*Math.sin(x*.011+z*.007)+6*Math.sin(x*.023-z*.017)+3*Math.sin(x*.05+z*.04);
  terrH=(x,z)=>{
    let sw=0,sy=0,dmin=1e9;
    for(let i=0;i<N;i+=2){const dx=x-TP[i][0],dz=z-TP[i][1],d2=dx*dx+dz*dz,k=1/((d2+1)*(d2+1));sw+=k;sy+=k*TY[i];if(d2<dmin)dmin=d2}
    const d=Math.sqrt(dmin),a=Math.exp(-Math.pow(Math.max(0,d-e0)/32,2));
    return (sy/sw-.4)*a+base(x,z)*(1-a);
  };
  const H=new Float32Array(gx*gz);
  for(let j=0;j<gz;j++)for(let i=0;i<gx;i++)H[j*gx+i]=terrH(x0+i*cell,z0+j*cell);
  const pos=new Float32Array(gx*gz*3),col=new Float32Array(gx*gz*3),ix=[];
  const sun=[-.45,.75,.35],sl=Math.hypot(...sun);
  const grass=[[.26,.42,.20],[.33,.50,.25]],rock=[.56,.53,.49],dirt=[.50,.45,.36];
  for(let j=0;j<gz;j++)for(let i=0;i<gx;i++){
    const k=j*gx+i,x=x0+i*cell,z=z0+j*cell,y=H[k];
    const hl=H[j*gx+Math.max(i-1,0)],hr=H[j*gx+Math.min(i+1,gx-1)],hu=H[Math.max(j-1,0)*gx+i],hd=H[Math.min(j+1,gz-1)*gx+i];
    let nx=(hl-hr)/(2*cell),nz=(hu-hd)/(2*cell),ny=1;const nl=Math.hypot(nx,ny,nz);nx/=nl;ny/=nl;nz/=nl;
    const sp=1-ny,rk=sm01((sp-.10)/.16),lit=clamp(.62+.5*((nx*sun[0]+ny*sun[1]+nz*sun[2])/sl),.55,1.12);
    const gv=.5+.5*Math.sin(x*.045)*Math.sin(z*.05),g=[grass[0][0]+(grass[1][0]-grass[0][0])*gv,grass[0][1]+(grass[1][1]-grass[0][1])*gv,grass[0][2]+(grass[1][2]-grass[0][2])*gv];
    for(let c3=0;c3<3;c3++)col[k*3+c3]=clamp((g[c3]*(1-rk)+rock[c3]*rk)*lit,0,1);
    pos[k*3]=x;pos[k*3+1]=y;pos[k*3+2]=z;
  }
  for(let j=0;j<gz-1;j++)for(let i=0;i<gx-1;i++){const a=j*gx+i,b=a+1,c=a+gx,d=c+1;ix.push(a,c,b,b,c,d)}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(pos,3));g.setAttribute('color',new THREE.BufferAttribute(col,3));g.setIndex(ix);
  MG.add(new THREE.Mesh(g,new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide})));
  /* 침엽수 */
  const nT=1100,variants=[spruceGeo({h:13,r:3.1,tiers:6}),spruceGeo({h:17,r:3.6,tiers:7}),spruceGeo({h:10,r:2.6,tiers:5})];
  const dm=new THREE.Object3D(),cc=new THREE.Color(),tm=new THREE.MeshBasicMaterial({vertexColors:true}),buckets=variants.map(()=>[]);
  let n=0,tries=0;
  while(n<nT&&tries<12000){tries++;
    const x=x0+pad*.5+Math.random()*(x1-x0-pad),z=z0+pad*.5+Math.random()*(z1-z0-pad);
    const [d]=nearD(x,z);if(d<HALF+18||d>100)continue;
    buckets[Math.floor(Math.random()*3)].push([x,terrH(x,z),z]);n++;
  }
  variants.forEach((vg,vi)=>{
    const L=buckets[vi],im=new THREE.InstancedMesh(vg,tm,Math.max(1,L.length));
    L.forEach((t,k)=>{const s=.75+Math.random()*.8;dm.position.set(t[0],t[1]-.3,t[2]);dm.rotation.set((Math.random()-.5)*.06,Math.random()*6.28,(Math.random()-.5)*.06);dm.scale.set(s,s*(.9+Math.random()*.35),s);dm.updateMatrix();im.setMatrixAt(k,dm.matrix);
      const v=.8+Math.random()*.4;cc.setRGB(v,v*(.95+Math.random()*.1),v*(.9+Math.random()*.15));im.setColorAt(k,cc)});
    im.count=L.length;MG.add(im);
  });
}
/* 크리스마스 트리 + 반짝이 전구 */
function buildXmasTrees(){
  const nT=170,vs=[spruceGeo({h:9,r:2.6,tiers:6,snow:true}),spruceGeo({h:12,r:3.2,tiers:7,snow:true})],lp=[],lc=[];
  const dm=new THREE.Object3D(),cc=new THREE.Color(),tm=new THREE.MeshBasicMaterial({vertexColors:true}),bk=[[],[]];
  const pal=[[255,70,60],[255,215,100],[90,170,255],[255,255,255],[120,255,160]];
  let n=0,tries=0;
  while(n<nT&&tries<6000){tries++;
    const i=Math.floor(Math.random()*N),sd=Math.random()<.5?-1:1,o=(HALF+9+Math.random()*50)*sd,q=TP[i],nn=TN[i];
    const x=q[0]+nn[0]*o,z=q[1]+nn[1]*o;
    const [d]=nearD(x,z);if(d<HALF+9)continue;
    const vi=Math.random()<.5?0:1,s=.8+Math.random()*.9,ys=1+Math.random()*.3,Hh=vi?12:9,Rr=vi?3.2:2.6;
    bk[vi].push([x,z,s,ys,Math.random()*6.28]);
    for(let L=0;L<9;L++){const yy=1.2+Math.random()*(Hh*.75),r=Rr*(1-yy/Hh)*s*.95,a=Math.random()*6.283,c=pal[Math.floor(Math.random()*pal.length)];
      lp.push(x+Math.cos(a)*r,yy*s*ys,z+Math.sin(a)*r);lc.push(c[0]/255,c[1]/255,c[2]/255)}
    n++;
  }
  vs.forEach((vg,vi)=>{const L=bk[vi],im=new THREE.InstancedMesh(vg,tm,Math.max(1,L.length));
    L.forEach((t,k)=>{dm.position.set(t[0],0,t[1]);dm.rotation.set(0,t[4],0);dm.scale.set(t[2],t[2]*t[3],t[2]);dm.updateMatrix();im.setMatrixAt(k,dm.matrix);const v=.85+Math.random()*.25;cc.setRGB(v,v,v);im.setColorAt(k,cc)});
    im.count=L.length;MG.add(im)});
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(lp,3));g.setAttribute('color',new THREE.Float32BufferAttribute(lc,3));
  MG.add(new THREE.Points(g,new THREE.PointsMaterial({size:1.5,map:glowTex(255,255,255),vertexColors:true,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,fog:false})));
}
function buildLamps(L){
  const pts=[],pos=[],nl=Math.floor(TLEN/L.gap);
  for(let k=0;k<nl;k++){const i=Math.floor(k/nl*N),sd=k%2?1:-1,o=((BR&&i>=BR.i0&&i<=BR.i1)?HALF+1.3:HALF+(WALL?WALL-HALF:0)+3.5)*sd,q=TP[i],n=TN[i];pts.push([q[0]+n[0]*o,q[1]+n[1]*o,TY[i]])}
  const post=new THREE.InstancedMesh(new THREE.CylinderGeometry(.12,.12,9,6),new THREE.MeshBasicMaterial({color:0x2a2d3a}),pts.length),d=new THREE.Object3D();
  pts.forEach((p,i)=>{d.position.set(p[0],p[2]+4.5,p[1]);d.updateMatrix();post.setMatrixAt(i,d.matrix);pos.push(p[0],p[2]+9.1,p[1])});
  MG.add(post);
  const cv=document.createElement('canvas');cv.width=cv.height=64;const gx=cv.getContext('2d');
  const gr=gx.createRadialGradient(32,32,0,32,32,32);gr.addColorStop(0,'rgba(255,236,190,1)');gr.addColorStop(.25,'rgba('+L.col+',.55)');gr.addColorStop(1,'rgba('+L.col+',0)');
  gx.fillStyle=gr;gx.fillRect(0,0,64,64);
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  MG.add(new THREE.Points(g,new THREE.PointsMaterial({size:L.size,map:new THREE.CanvasTexture(cv),transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,fog:false,sizeAttenuation:true})));
}
function railTex(kind){
  if(kind==='guard')return mkTex(128,64,(x,w,h)=>{
    x.fillStyle='#4b5058';x.fillRect(6,22,7,42);
    x.fillStyle='#d4d9df';x.fillRect(0,6,w,15);x.fillRect(0,26,w,12);
    x.fillStyle='#8b939c';x.fillRect(0,19,w,3);x.fillRect(0,36,w,2);
    x.fillStyle='#f08a24';x.fillRect(6,8,7,11);});
  if(kind==='jersey')return mkTex(128,64,(x,w,h)=>{
    x.fillStyle='#9a9ea8';x.fillRect(0,0,w,h);
    x.fillStyle='#82868f';x.fillRect(0,38,w,26);x.fillStyle='#b9bcc5';x.fillRect(0,0,w,9);
    x.fillStyle='#6e727b';x.fillRect(0,36,w,3);x.fillStyle='#777b84';x.fillRect(0,0,2,h);x.fillRect(64,0,2,h);
    x.fillStyle='#ffb020';x.fillRect(28,14,16,8);x.fillStyle='#fff';x.fillRect(92,14,16,8);});
  return mkTex(128,64,(x,w,h)=>{
    x.fillStyle='#6b4a2b';x.fillRect(5,14,10,50);x.fillRect(0,12,w,8);x.fillRect(0,32,w,8);
    x.fillStyle='#8a6439';x.fillRect(0,12,w,3);x.fillRect(0,32,w,3);
    x.fillStyle='#fff';x.fillRect(5,14,10,3);
    for(let X=6;X<w;X+=14){x.fillStyle=['#ffd45c','#ff6b5e','#6bb4ff','#fff3c9'][(X/14|0)%4];x.beginPath();x.arc(X,24,3,0,7);x.fill()}});
}


/* 다리: 가장 곧은 구간을 골라 도로를 들어 올리고, 아래로 강을 흐르게 해요 */
function planBridge(){
  const R=85,hw=35,H=9;let best=1e9,c=300;
  for(let i=250;i<N-250;i++){let sum=0;for(let k=-R;k<R;k+=5){let d=TH[i+k+5]-TH[i+k];d=Math.atan2(Math.sin(d),Math.cos(d));sum+=Math.abs(d)}if(sum<best){best=sum;c=i}}
  for(let i=c-R;i<=c+R;i++){const d=Math.abs(i-c);TY[i]=H*(d<=hw?1:sm01((R-d)/(R-hw)))}
  const hd=[Math.cos(TH[c]),Math.sin(TH[c])],nn=TN[c],cx=TP[c][0],cz=TP[c][1];
  let vmax=650,vmin=-650;
  for(let j=0;j<N;j++){if(j>=c-R-30&&j<=c+R+30)continue;const dx=TP[j][0]-cx,dz=TP[j][1]-cz,u=dx*hd[0]+dz*hd[1],v=dx*nn[0]+dz*nn[1];
    if(Math.abs(u)<85){if(v>0)vmax=Math.min(vmax,v-45);else vmin=Math.max(vmin,v+45)}}
  vmax=Math.max(vmax,90);vmin=Math.min(vmin,-90);
  BR={c,i0:c-R,i1:c+R,H,hd,nn,cx,cz,vmin,vmax};
  RIVER={a:[cx+nn[0]*vmin,cz+nn[1]*vmin],b:[cx+nn[0]*vmax,cz+nn[1]*vmax]};
}
function buildBridge(){
  const {i0,i1,hd,nn,cx,cz,vmin,vmax}=BR,off=HALF+2.6;
  strip(-off,off,-.55,()=>[0,0],new THREE.MeshBasicMaterial({color:0x6f7480,side:THREE.DoubleSide}));
  const gm=new THREE.MeshBasicMaterial({color:0x8a8f9b,side:THREE.DoubleSide});
  wallStrip(off,1.6,gm,6,i0,i1,-1.6);wallStrip(-off,1.6,gm,6,i0,i1,-1.6);
  const pts=[];for(let i=i0;i<=i1;i+=22)if(TY[i]>1.2)pts.push(i);
  const im=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshBasicMaterial({color:0x666b77}),pts.length),d=new THREE.Object3D();
  pts.forEach((i,k)=>{const hh=TY[i]-.55;d.position.set(TP[i][0],hh/2,TP[i][1]);d.rotation.set(0,-TH[i],0);d.scale.set(3.4,hh,2*off-2);d.updateMatrix();im.setMatrixAt(k,d.matrix)});
  MG.add(im);
  /* 강 */
  WATERT=mkTex(128,128,(x,w,h)=>{
    const g=x.createLinearGradient(0,0,0,h);g.addColorStop(0,'#0a1630');g.addColorStop(1,'#12254a');x.fillStyle=g;x.fillRect(0,0,w,h);
    for(let k=0;k<70;k++){const y=Math.random()*h,len=8+Math.random()*40,xx=Math.random()*w,c=['255,176,80','255,230,170','120,170,255','255,120,90'][k%4];
      x.fillStyle='rgba('+c+','+(.12+Math.random()*.3)+')';x.fillRect(xx,y,len,1+Math.random()*1.5);x.fillRect(xx-w,y,len,1.5)}});
  const W2=55,P=[[-W2,vmin],[W2,vmin],[W2,vmax],[-W2,vmax]],pos=[],uv=[];
  P.forEach(([u,v])=>{pos.push(cx+hd[0]*u+nn[0]*v,.05,cz+hd[1]*u+nn[1]*v);uv.push(v/70,u/70)});
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex([0,1,2,0,2,3]);
  MG.add(new THREE.Mesh(g,new THREE.MeshBasicMaterial({map:WATERT,side:THREE.DoubleSide})));
}

function setMap(id){
  if(!MAPS[id])id='seoul';const D=MAPS[id];
  clearMap();MAPID=id;MG=new THREE.Group();S.add(MG);
  HALF=D.half;WALL=D.wall?HALF+D.wall:0;
  TP=D.pts();TY=D.elev?elev(...D.elev):new Array(N).fill(0);
  TS=[0];TN=[];TH=[];
  for(let i=1;i<=N;i++){const a=TP[i%N],b=TP[i-1];TS.push(TS[i-1]+Math.hypot(a[0]-b[0],a[1]-b[1]))}
  TLEN=TS[N];
  for(let i=0;i<N;i++){const a=TP[(i+N-1)%N],b=TP[(i+1)%N],dx=b[0]-a[0],dz=b[1]-a[1],l=Math.hypot(dx,dz);
    TH.push(Math.atan2(dz,dx));TN.push([-dz/l,dx/l])}
  BR=null;RIVER=null;WATERT=null;if(D.bridge)planBridge();
  TSL=[];for(let i=0;i<N;i++)TSL.push((TY[(i+4)%N]-TY[(i+N-4)%N])/(8*TLEN/N));
  sx=TP[0][0];sz=TP[0][1];sh=TH[0];
  S.background=new THREE.Color(D.bg);S.fog=new THREE.Fog(D.fog[0],D.fog[1],D.fog[2]);
  gnd.material.color.setHex(D.gnd);gnd.position.y=D.gy;
  skyMat.map=skyTex(id);skyMat.needsUpdate=true;
  document.documentElement.style.setProperty('--sky','url("'+SKIES[id]+'")');
  /* 도로 */
  if(D.terrain)buildTerrain();
  if(D.shoulder){const sm=new THREE.MeshBasicMaterial({color:D.shoulder,side:THREE.DoubleSide});strip(HALF,WALL+1.2,.01,()=>[0,0],sm);strip(-WALL-1.2,-HALF,.01,()=>[0,0],sm)}
  strip(-HALF,HALF,0,(i,s)=>[s*1.6,TS[i]/10],new THREE.MeshBasicMaterial({map:asphT,color:D.asph,side:THREE.DoubleSide}));
  const kerbT=mkTex(64,8,(x)=>{x.fillStyle=D.kerb[0];x.fillRect(0,0,32,8);x.fillStyle=D.kerb[1];x.fillRect(32,0,32,8)});
  const kerbM=new THREE.MeshBasicMaterial({map:kerbT,color:0xc8c8d0,side:THREE.DoubleSide});
  strip(HALF,HALF+1.4,.02,(i,s)=>[TS[i]/4,s],kerbM);
  strip(-HALF-1.4,-HALF,.02,(i,s)=>[TS[i]/4,s],kerbM);
  const dashT=mkTex(8,64,(x)=>{x.fillStyle='#fff';x.fillRect(0,0,8,26)});
  strip(-.18,.18,.03,(i,s)=>[s,TS[i]/8],new THREE.MeshBasicMaterial({map:dashT,transparent:true,opacity:.75,depthWrite:false,side:THREE.DoubleSide}));
  /* 바리케이드 */
  if(BR)buildBridge();
  if(D.rail){
    const mk=k=>new THREE.MeshBasicMaterial({map:railTex(k),transparent:true,alphaTest:.5,side:THREE.DoubleSide,color:k==='fence'?0xdcd6cc:0xffffff});
    const hOf=k=>k==='guard'?.9:k==='jersey'?.95:1.05;
    const segs=BR?[[0,BR.i0,D.rail,0],[BR.i0,BR.i1,'guard',1],[BR.i1,N,D.rail,0]]:[[0,N,D.rail,0]];
    segs.forEach(([a,b,k,br])=>{const m=mk(k),hh=br?1.15:hOf(k);wallStrip(WALL+.35,hh,m,4,a,b);wallStrip(-WALL-.35,hh,m,4,a,b)});
    if(D.rail==='fence'){ /* 울타리 위 전구 */
      const lp=[],lc=[],pal=[[255,214,120],[255,110,100],[120,190,255],[255,245,210]];
      for(let i=0;i<N;i+=3)for(const sd of[-1,1]){const n=TN[i],q=TP[i],o=(WALL+.35)*sd;lp.push(q[0]+n[0]*o,TY[i]+.72,q[1]+n[1]*o);const c=pal[(i/3|0)%4];lc.push(c[0]/255,c[1]/255,c[2]/255)}
      const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(lp,3));g.setAttribute('color',new THREE.Float32BufferAttribute(lc,3));
      MG.add(new THREE.Points(g,new THREE.PointsMaterial({size:1.3,map:glowTex(255,255,255),vertexColors:true,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,fog:false})));
    }
  }
  if(D.trees)buildXmasTrees();
  if(D.lamps)buildLamps(D.lamps);
  /* 출발선 + 게이트 */
  const line=new THREE.Mesh(new THREE.PlaneGeometry(1.6,HALF*2),new THREE.MeshBasicMaterial({color:0xffffff}));
  line.rotation.x=-Math.PI/2;line.rotation.z=-sh;line.position.set(sx,TY[0]+.04,sz);MG.add(line);
  const yel=new THREE.MeshBasicMaterial({color:0xf2c230});
  [-1,1].forEach(sd=>{const m=new THREE.Mesh(new THREE.BoxGeometry(.5,7,.5),yel);m.position.set(sx+TN[0][0]*(HALF+1.5)*sd,TY[0]+3.5,sz+TN[0][1]*(HALF+1.5)*sd);MG.add(m)});
  const gb=new THREE.Mesh(new THREE.BoxGeometry(.5,1,(HALF+1.5)*2),yel);gb.position.set(sx,TY[0]+7,sz);gb.rotation.y=-sh;MG.add(gb);
  /* 상태 초기화 */
  bestLap=null;$('best').textContent='-';$('last').textContent='-';$('send').disabled=true;
  $('msg').textContent='한 바퀴를 완주하면 올릴 수 있어요.';
  reset();mmSetup();
  document.querySelectorAll('.maps button').forEach(b=>b.setAttribute('aria-checked',b.dataset.map===id));
  try{localStorage.setItem('drift-map',id)}catch(e){}
}

""".replace('%SEOUL%',seoul).replace('%SKYM%',b64('sky_mountain.webp','image/webp')).replace('%SKYX%',b64('sky_xmas.webp','image/webp')).replace('%CORE%',core).replace('%ASPH%',asph)

h=h[:a]+new.lstrip('\n')+h[b:]

# ---- 2) 상수였던 변수들 ----
def rep1(old,newv,cnt=1):
    global h
    assert h.count(old)==cnt,(old,h.count(old))
    h=h.replace(old,newv)

# 이전 블록에 있던 S.fog 초기값은 setMap이 덮어씀. 물리: 변수 추가
rep1("let c,steer,ci,prog,lapStart,","let camY=0,camP=0,hitK=0,lastThump=0,c,steer,ci,prog,lapStart,")
rep1("c={x:sx,z:sz,h:sh,vx:0,vz:0};steer=0;","c={x:sx,z:sz,h:sh,vx:0,vz:0};steer=0;camY=TY[0]||0;camP=0;hitK=0;")

# 충돌 소리
rep1("let slip=0;\nfunction step(dt){","""let slip=0;
function thump(v){
  const t=performance.now();if(t-lastThump<160||!AC||AC.state!=='running')return;lastThump=t;
  const n=AC.sampleRate*.2|0,b=AC.createBuffer(1,n,AC.sampleRate),d=b.getChannelData(0);
  for(let i=0;i<n;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/n,3);
  const s=AC.createBufferSource();s.buffer=b;const f=AC.createBiquadFilter();f.type='lowpass';f.frequency.value=420;
  const g=AC.createGain();g.gain.value=.55*v;s.connect(f);f.connect(g);g.connect(AC.destination);s.start();
}
function step(dt){""")
# 경사: 내리막에서는 빨라지고 오르막에서는 느려져요
rep1("  if(keys.brake)vf-=(vf>0.5?24:7)*dt;","  vf-=9.8*.55*TSL[ci]*Math.cos(c.h-TH[ci])*dt;\n  if(keys.brake)vf-=(vf>0.5?24:7)*dt;")
# 벽 충돌
rep1("  const LIM=HALF+22;\n  if(Math.abs(side)>LIM){","""  if(WALL&&Math.abs(side)>WALL){
    const n=TN[ci],sg=side>0?1:-1,over=Math.abs(side)-WALL;
    c.x-=n[0]*sg*over;c.z-=n[1]*sg*over;
    const vn=c.vx*n[0]*sg+c.vz*n[1]*sg;
    if(vn>0){
      c.vx-=n[0]*sg*vn*1.3;c.vz-=n[1]*sg*vn*1.3;
      const k=Math.max(.5,1-vn*.02);c.vx*=k;c.vz*=k;
      let dh=TH[ci]-c.h;dh=Math.atan2(Math.sin(dh),Math.cos(dh));c.h+=dh*Math.min(.5,vn*.04);
      hitK=Math.min(1,Math.max(hitK,vn/14));if(vn>2.5)thump(Math.min(1,vn/14));
    }
  }
  const LIM=HALF+22;
  if(!WALL&&Math.abs(side)>LIM){""")
# 랩 기록 전송 (서울만)
rep1("$('send').disabled=false;\n        $('msg').textContent='새 기록이에요! 이름을 적고 올려보세요.';","$('send').disabled=MAPID!=='seoul';\n        $('msg').textContent=MAPID==='seoul'?'새 기록이에요! 이름을 적고 올려보세요.':'새 기록이에요! (이 맵 순위표는 아직 준비 중이에요)';")
# 미니맵 가드 + 초기 맵
rep1("function mmSetup(){\n","function mmSetup(){\n  if(!TP.length)return;\n")
rep1("mmSetup();addEventListener('resize',mmSetup);","mmSetup();addEventListener('resize',mmSetup);\nlet _m0='seoul';try{_m0=localStorage.getItem('drift-map')||'seoul'}catch(e){}\nsetMap(_m0);")
# 카메라: 고도
rep1("  cam.position.set(c.x+rx*.36+fx*.15,1.15+bump,c.z+rz*.36+fz*.15);\n  cam.rotation.set(-.15,","  camY+=((TY[ci]||0)-camY)*Math.min(1,dt*10);camP+=((TSL[ci]||0)-camP)*Math.min(1,dt*3);\n  cam.position.set(c.x+rx*.36+fx*.15,camY+1.15+bump,c.z+rz*.36+fz*.15);\n  cam.rotation.set(-.15+Math.atan(camP)*Math.cos(c.h-TH[ci]),")
rep1("  const fov=62+20*nitroK;","  if(hitK>0){hitK=Math.max(0,hitK-dt*3.5);cam.position.x+=(Math.random()-.5)*.12*hitK;cam.position.y+=(Math.random()-.5)*.08*hitK;cam.rotation.z+=(Math.random()-.5)*.03*hitK}\n  const fov=62+20*nitroK;")
rep1("sky.position.set(cam.position.x,SKY_Y,cam.position.z);","sky.position.set(cam.position.x,cam.position.y+SKY_Y-1.15,cam.position.z);if(WATERT)WATERT.offset.x+=dt*.012;")
rep1("mbg.clearRect(0,0,mw,mh);mbg.lineJoin='round';mbg.lineCap='round';","mbg.clearRect(0,0,mw,mh);mbg.lineJoin='round';mbg.lineCap='round';\n  if(RIVER){mbg.strokeStyle='#2a58c4';mbg.lineWidth=10*mdpr;mbg.beginPath();mbg.moveTo(RIVER.a[0]*msc+mox,RIVER.a[1]*msc+moz);mbg.lineTo(RIVER.b[0]*msc+mox,RIVER.b[1]*msc+moz);mbg.stroke()}")
rep1("beam.position.set(c.x+fx*22,.06,c.z+fz*22);","beam.position.set(c.x+fx*22,camY+.06,c.z+fz*22);")

# ---- 3) 홈 UI ----
rep1("#start .cta{","""#start .maps{display:flex;gap:10px;width:min(100%,560px);padding:0 10px;box-sizing:border-box}
#start .maps button{flex:1;min-width:0;padding:0;background:#0b0d14;border:2px solid var(--line);border-radius:10px;overflow:hidden;color:#8d96a3;cursor:pointer;text-align:left;display:flex;flex-direction:column;transition:border-color .12s,color .12s,transform .12s}
#start .maps button:hover{transform:translateY(-2px)}
#start .maps img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;opacity:.6;transition:opacity .15s}
#start .maps b{display:block;font-size:clamp(12px,1.9vh,14px);padding:7px 8px 0;line-height:1.2;color:inherit;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#start .maps em{font-style:normal;font-size:11px;padding:2px 8px 7px;color:#8d96a3}
#start .maps button[aria-checked=true]{border-color:var(--gold);color:#fff;background:#1a1810}
#start .maps button[aria-checked=true] img{opacity:1}
#start .maps button[aria-checked=true] em{color:var(--gold)}
#start .maps button:focus-visible{outline:3px solid #fff;outline-offset:2px}
@media (max-height:520px){#start .maps img{aspect-ratio:3/1}#start .maps em{display:none}#start .maps b{padding-bottom:6px}}
#start .cta{""")
rep1("max-height:46vh;","max-height:min(40vh,calc(100vh - 330px));")
rep1("""    <div class="cta">
      <button class="btn play" id="go">""","""    <div class="maps" role="radiogroup" aria-label="맵 선택">
      <button role="radio" aria-checked="true" data-map="seoul"><img src="%T1%" alt=""><b>Seoul</b><em>보통 · 야경 도심</em></button>
      <button role="radio" aria-checked="false" data-map="mountain"><img src="%T2%" alt=""><b>Mountain Pass</b><em>어려움 · 내리막 산길</em></button>
      <button role="radio" aria-checked="false" data-map="xmas"><img src="%T3%" alt=""><b>Christmas</b><em>쉬움 · 눈 내리는 밤</em></button>
    </div>
    <div class="cta">
      <button class="btn play" id="go">""".replace('%T1%',b64('thumb_seoul.webp','image/webp')).replace('%T2%',b64('thumb_mountain.webp','image/webp')).replace('%T3%',b64('thumb_xmas.webp','image/webp')))
rep1("$('lbBtn').onclick=()=>openLeaderboard();","$('lbBtn').onclick=()=>openLeaderboard();\ndocument.querySelectorAll('.maps button').forEach(b=>b.onclick=()=>{if(b.dataset.map!==MAPID)setMap(b.dataset.map)});")

open(W+'t_maps.html','w',encoding='utf-8').write(h)
print('built',len(h))
