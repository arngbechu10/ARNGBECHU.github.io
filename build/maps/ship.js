
/* ================= 화물선 탈출 맵 (편도 코스 + 점프) ================= */
/* 공중 상태·장애물·편도 결승 지점. 다른 맵에서는 JMP=null, OBS=[], LAPEND=N */
var AIR=false,cy=0,cvy=0,OBS=[],JMP=null,LAPEND=1400,OPENP=false,SP=1;
const SH={L:525,deckY:10.5,quayY:3,xR0:340,xLip:364,rampY:4.2,xLand:412,xFin:512,hullW:24};
const OCEAN_URI='%OCEAN%';
function shipPts(){const a=[];for(let i=0;i<N;i++)a.push([SH.L*i/(N-1),0]);return a}
function shipTY(){
  const a=[];
  for(let i=0;i<N;i++){const x=SH.L*i/(N-1);
    a.push(x<SH.xR0?SH.deckY:x<=SH.xLip?SH.deckY+SH.rampY*(x-SH.xR0)/(SH.xLip-SH.xR0):x<SH.xLand?SH.deckY+SH.rampY:SH.quayY)}
  return a;
}
/* 점프에 필요한 최소 속도 (램프 끝에서 이륙해 부두 끝을 넘으려면) */
function needSpeed(){
  const sl=SH.rampY/(SH.xLip-SH.xR0),dh=SH.deckY+SH.rampY-SH.quayY,G=SH.xLand-SH.xLip;
  for(let v=5;v<80;v+=.25){const vy=v*sl,t=(vy+Math.sqrt(vy*vy+2*9.8*dh))/9.8;if(v*t>=G+1)return v}
  return 80;
}
function shipPlan(){
  const sp=SH.L/(N-1),iX=x=>Math.max(0,Math.min(N-1,Math.round(x/sp)));
  const v=needSpeed();
  JMP={iLip:iX(SH.xLip),iLand:iX(SH.xLand),slope:SH.rampY/(SH.xLip-SH.xR0),needKmh:Math.ceil(v*3.6/5)*5};
  LAPEND=iX(SH.xFin);
  /* 장애물: 가로로 놓인 컨테이너가 좌우 번갈아 길을 막고, 남은 틈에 드럼통 */
  OBS=[];const W=WALL;
  for(let k=0;k<10;k++){
    const x=62+k*26+(k%3)*2,sg=k%2?1:-1;
    OBS.push({x,z:sg*(W-6.1),hx:1.22,hz:6.1,h:k%3===2?5.2:2.6,type:'box',col:CPAL[(k*3)%CPAL.length]});
    if(k%2===1)OBS.push({x:x+9,z:-sg*5.6,hx:.95,hz:.95,h:1.2,type:'drum'});
  }
  /* 보이지 않는 막이: 배 뒤쪽, 부두 끝(뒤로 떨어지지 않게) */
  OBS.push({x:-14,z:0,hx:2,hz:30,h:3,type:'inv',soft:true});
  OBS.push({x:SH.xLand-2.5,z:0,hx:.3,hz:W+3,h:2,type:'inv',soft:true});
}
const CPAL=['#e2603a','#d9472f','#2c6db4','#1e4f94','#f1c232','#e8a02a','#3aa58f','#d6dadd','#8a2e3a','#2e8bb5','#c2502c','#f0f0ee'];
/* 범위가 있는 도로 띠 (편도 코스용) */
function strip2(o1,o2,y,i0,i1,uvf,mat){
  const p=[],uv=[],ix=[];
  for(let i=i0;i<=i1;i++){const n=TN[i],q=TP[i];
    p.push(q[0]+n[0]*o1,y+TY[i],q[1]+n[1]*o1,q[0]+n[0]*o2,y+TY[i],q[1]+n[1]*o2);uv.push(...uvf(i,0),...uvf(i,1))}
  for(let i=0;i<i1-i0;i++){const k=i*2;ix.push(k,k+1,k+2,k+1,k+3,k+2)}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(ix);
  const m=new THREE.Mesh(g,mat);MG.add(m);return m;
}
/* 면마다 밝기가 다른 상자 (조명 없이도 입체감) */
function shadedBox(){
  const g=new THREE.BoxGeometry(1,1,1),sh=[.74,.62,1,.4,.88,.8],col=[];
  for(let f=0;f<6;f++)for(let v=0;v<4;v++)col.push(sh[f],sh[f],sh[f]);
  g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));return g;
}
function buildShip(){
  const {deckY,quayY,xR0,xLip,xLand,xFin,hullW}=SH,W=WALL;
  const iR0=Math.round(xR0/(SH.L/(N-1))),iLip=JMP.iLip,iLand=JMP.iLand;
  const M=o=>new THREE.MeshBasicMaterial(o);
  /* 바다: 보내준 사진의 바다 질감 */
  const oc=TL.load(OCEAN_URI);oc.wrapS=oc.wrapT=THREE.MirroredRepeatWrapping;oc.repeat.set(110,110);
  gnd.material.map=oc;gnd.material.color.setHex(0xffffff);gnd.material.needsUpdate=true;WATERT=oc;
  /* 선체 */
  const len=xLip+30,cx=(xLip-30)/2;
  const up=new THREE.Mesh(new THREE.BoxGeometry(len,deckY-3.3,hullW*2),M({color:0x23324a}));up.position.set(cx,3.3+(deckY-3.3)/2-.05,0);MG.add(up);
  const lo=new THREE.Mesh(new THREE.BoxGeometry(len,3.6,hullW*2-.6),M({color:0x8a2b25}));lo.position.set(cx,1.6,0);MG.add(lo);
  const deckT=mkTex(128,128,(x,w,h)=>{x.fillStyle='#5f6a74';x.fillRect(0,0,w,h);x.fillStyle='#56606a';x.fillRect(0,0,w/2,h/2);x.fillRect(w/2,h/2,w/2,h/2);
    x.fillStyle='#3d454e';x.fillRect(0,0,w,2);x.fillRect(0,0,2,h);for(let k=0;k<30;k++){x.fillStyle='rgba(120,70,40,'+(.08+Math.random()*.12)+')';x.fillRect(Math.random()*w,Math.random()*h,2+Math.random()*10,1+Math.random()*3)}});
  deckT.repeat.set(len/14,hullW*2/14);
  const dk=new THREE.Mesh(new THREE.PlaneGeometry(len,hullW*2),M({map:deckT}));dk.rotation.x=-Math.PI/2;dk.position.set(cx,deckY-.04,0);MG.add(dk);
  /* 갑판 차선 (출발 ~ 램프 끝) */
  const laneT=mkTex(128,64,(x,w,h)=>{x.fillStyle='#454d59';x.fillRect(0,0,w,h);x.fillStyle='#f2c230';x.fillRect(3,0,5,h);x.fillRect(w-8,0,5,h);x.fillStyle='#e9eaf0';x.fillRect(62,0,4,h*.45)});
  strip2(-W,W,.02,0,iLip,(i,s)=>[s,TS[i]/9],M({map:laneT,side:THREE.DoubleSide}));
  /* 램프: 노랑·검정 경고 줄무늬 + 옆면 */
  const hz=mkTex(64,64,(x,w,h)=>{x.fillStyle='#1b1d22';x.fillRect(0,0,w,h);x.fillStyle='#f2c230';for(let k=-2;k<4;k++){x.beginPath();x.moveTo(k*32,0);x.lineTo(k*32+16,0);x.lineTo(k*32+16+h,h);x.lineTo(k*32+h,h);x.fill()}});
  strip2(-W,W,.04,iR0,iLip,(i,s)=>[s*4,TS[i]/4],M({map:hz,side:THREE.DoubleSide}));
  const side=sg=>{const z=sg*W,p=[xR0,deckY,z,xLip,deckY,z,xLip,deckY+SH.rampY,z],g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));MG.add(new THREE.Mesh(g,M({color:0x2c3038,side:THREE.DoubleSide})))};
  side(-1);side(1);
  const fr=new THREE.Mesh(new THREE.PlaneGeometry(W*2,SH.rampY),M({map:hz,side:THREE.DoubleSide}));fr.rotation.y=Math.PI/2;fr.position.set(xLip+.02,deckY+SH.rampY/2,0);MG.add(fr);
  /* 부두 */
  const qL=xFin-xLand+160,qcx=xLand+qL/2;
  const q=new THREE.Mesh(new THREE.BoxGeometry(qL,quayY+.2,90),M({color:0x6c727b}));q.position.set(qcx,(quayY+.2)/2-.2,12);MG.add(q);
  const conT=mkTex(128,128,(x,w,h)=>{x.fillStyle='#9aa0a8';x.fillRect(0,0,w,h);for(let k=0;k<160;k++){const v=140+Math.random()*30|0;x.fillStyle='rgb('+v+','+v+','+(v+4)+')';x.fillRect(Math.random()*w,Math.random()*h,2,2)}x.fillStyle='#80868e';x.fillRect(0,0,w,2);x.fillRect(0,0,2,h)});
  conT.repeat.set(qL/10,9);
  const qt=new THREE.Mesh(new THREE.PlaneGeometry(qL,90),M({map:conT,color:0xa4a9b0}));qt.rotation.x=-Math.PI/2;qt.position.set(qcx,quayY+.01,12);MG.add(qt);
  const qlaneT=mkTex(128,64,(x,w,h)=>{x.fillStyle='#3e434b';x.fillRect(0,0,w,h);x.fillStyle='#e9eaf0';x.fillRect(3,0,4,h);x.fillRect(w-7,0,4,h);x.fillStyle='#f2c230';x.fillRect(62,0,4,h*.5)});
  strip2(-W,W,.03,iLand,N-1,(i,s)=>[s,TS[i]/9],M({map:qlaneT,side:THREE.DoubleSide}));
  /* 부두 가장자리 노란 선 + 방호벽 */
  const edge=new THREE.Mesh(new THREE.PlaneGeometry(.6,90),M({color:0xf2c230}));edge.rotation.x=-Math.PI/2;edge.position.set(xLand+.3,quayY+.03,12);MG.add(edge);
  const jm=M({map:railTex('jersey'),transparent:true,alphaTest:.5,side:THREE.DoubleSide});
  wallStrip(W+.35,.95,jm,4,iLand,N-1);wallStrip(-W-.35,.95,jm,4,iLand,N-1);
  wallStrip(W+.35,.95,jm,4,Math.round(300/(SH.L/(N-1))),iR0);wallStrip(-W-.35,.95,jm,4,Math.round(300/(SH.L/(N-1))),iR0);
  /* 컨테이너 더미 (배 위 양옆 + 부두 오른쪽) */
  const ct=mkTex(64,32,(x,w,h)=>{x.fillStyle='#fff';x.fillRect(0,0,w,h);x.fillStyle='rgba(0,0,0,.16)';for(let X=1;X<w;X+=4)x.fillRect(X,0,1.6,h);x.fillStyle='rgba(0,0,0,.32)';x.fillRect(0,0,w,2);x.fillRect(0,h-2,w,2);x.fillRect(0,0,2,h);x.fillRect(w-2,0,2,h)});
  const list=[],cc=new THREE.Color();
  const rnd=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(77);
  for(let bx=-24;bx<300;bx+=12.6)for(const sg of[-1,1])for(let col=0;col<6;col++){
    const z=sg*(W+.4+1.25+col*2.56);if(Math.abs(z)>hullW-1.3)continue;
    if(col>0&&rnd()<.12)continue;
    const n=col===0?4+(rnd()*2|0):2+(rnd()*4|0);
    for(let k=0;k<n;k++)list.push([bx+6.3,deckY+1.3+k*2.6,z,12.19,2.59,2.44,CPAL[(rnd()*CPAL.length)|0]]);
  }
  for(let bx=xLand+20;bx<xFin+120;bx+=12.6)for(let col=0;col<4;col++){const z=W+8+col*2.56,n=1+(rnd()*3|0);
    for(let k=0;k<n;k++)list.push([bx,quayY+1.3+k*2.6,z,12.19,2.59,2.44,CPAL[(rnd()*CPAL.length)|0]])}
  /* 길을 막는 장애물 컨테이너 */
  OBS.forEach(o=>{if(o.type!=='box')return;const n=Math.round(o.h/2.6);for(let k=0;k<n;k++)list.push([o.x,deckY+1.3+k*2.6,o.z,o.hx*2,2.59,o.hz*2,o.col])});
  const im=new THREE.InstancedMesh(shadedBox(),M({map:ct,vertexColors:true}),list.length),d=new THREE.Object3D();
  list.forEach((b,k)=>{d.position.set(b[0],b[1],b[2]);d.scale.set(b[3],b[4],b[5]);d.updateMatrix();im.setMatrixAt(k,d.matrix);cc.set(b[6]);im.setColorAt(k,cc)});
  MG.add(im);
  /* 드럼통 */
  const drums=OBS.filter(o=>o.type==='drum'),dg=new THREE.CylinderGeometry(.42,.42,1.15,14),dm=new THREE.InstancedMesh(dg,M({color:0x1f6fb2}),drums.length*3);
  let di=0;drums.forEach(o=>{[[-.45,-.45],[.45,-.3],[0,.45]].forEach(([ax,az])=>{d.position.set(o.x+ax,deckY+.58,o.z+az);d.scale.set(1,1,1);d.updateMatrix();dm.setMatrixAt(di++,d.matrix)})});
  MG.add(dm);
  /* 갠트리 크레인 (부두) */
  const cm=M({color:0xd9482f}),cm2=M({color:0xb53a24});
  [[xLand+40],[xLand+95]].forEach(([x])=>{
    [[-6,W+3],[6,W+3],[-6,W+30],[6,W+30]].forEach(([dx,z])=>{const l=new THREE.Mesh(new THREE.BoxGeometry(1.2,38,1.2),cm);l.position.set(x+dx,quayY+19,z);MG.add(l)});
    const bm=new THREE.Mesh(new THREE.BoxGeometry(3,3,70),cm2);bm.position.set(x,quayY+39,W-8);MG.add(bm);
    const cab=new THREE.Mesh(new THREE.BoxGeometry(5,3,4),M({color:0xe8e8ea}));cab.position.set(x,quayY+36,W-20);MG.add(cab);
  });
  /* 결승선: 체크무늬 + 게이트 */
  const ck=mkTex(64,16,(x,w,h)=>{for(let X=0;X<w;X+=8)for(let Y=0;Y<h;Y+=8){x.fillStyle=((X+Y)/8)%2?'#111':'#fff';x.fillRect(X,Y,8,8)}});
  const fl=new THREE.Mesh(new THREE.PlaneGeometry(2.4,W*2),M({map:ck}));fl.rotation.x=-Math.PI/2;fl.position.set(xFin,quayY+.05,0);MG.add(fl);
  const ym=M({color:0xf2c230});
  [-1,1].forEach(sg=>{const m=new THREE.Mesh(new THREE.BoxGeometry(.5,7,.5),ym);m.position.set(xFin,quayY+3.5,sg*(W+1.5));MG.add(m)});
  const gb=new THREE.Mesh(new THREE.BoxGeometry(.5,1.2,(W+1.5)*2),M({map:ck}));gb.position.set(xFin,quayY+7,0);MG.add(gb);
}
/* 장애물 충돌 (월드 좌표 상자, 차는 길이 4.4m × 폭 2m로 근사) */
function obsCollide(){
  for(const o of OBS){
    const dx=c.x-o.x,dz=c.z-o.z,px=o.hx+2.2-Math.abs(dx),pz=o.hz+1-Math.abs(dz);
    if(px<=0||pz<=0)continue;
    let vin;
    if(pz<px){const sg=dz>=0?1:-1;c.z+=sg*pz;vin=-c.vz*sg;if(vin>0)c.vz+=sg*vin*1.3}
    else{const sg=dx>=0?1:-1;c.x+=sg*px;vin=-c.vx*sg;if(vin>0){c.vx+=sg*vin*1.25;c.vz*=.7}}
    if(vin>0&&!o.soft){
      hitK=Math.min(1,Math.max(hitK,vin/12));if(vin>2)thump(Math.min(1,vin/14));
      if(MODE==='hard'&&vin>3.5)wallHit();
    }
  }
}
/* 점프 */
function launch(vf){AIR=true;cy=TY[ci];cvy=Math.max(0,vf)*JMP.slope}
function airStep(dt){
  steer+=(((keys.right?1:0)-(keys.left?1:0))-steer)*Math.min(1,dt*5);
  c.x+=c.vx*dt;c.z+=c.vz*dt;cvy-=9.8*dt;cy+=cvy*dt;
  const ni=nearest(c.x,c.z,ci,70);let di=ni-ci;if(di>N/2)di-=N;if(di<-N/2)di+=N;ci=ni;prog+=di;if(prog<0)prog=0;
  if(cy<=SH.quayY){
    if(ci>=JMP.iLand&&Math.abs(side)<WALL+.8){
      AIR=false;const imp=-cvy;cy=TY[ci];cvy=0;c.vx*=.9;c.vz*=.9;
      hitK=Math.min(1,Math.max(hitK,imp/13));thump(Math.min(1,imp/12));
    }else onWater();
  }
}
function onWater(){
  if(MODE==='hard'&&typeof hardWater==='function')hardWater();
  else reset();
}
