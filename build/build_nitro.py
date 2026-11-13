import re
h=open('t_edit.html',encoding='utf-8').read()
def rep(a,b):
    global h
    assert h.count(a)==1,(h.count(a),a[:90]);h=h.replace(a,b)

# ---------- CSS ----------
rep("#start .edit{display:flex;", """#fx{position:fixed;inset:0;width:100%;height:100%;pointer-events:none}
#nit{position:fixed;left:10px;top:158px;width:210px;box-sizing:border-box;padding:7px 10px 8px;border-radius:10px;background:#0b0d14cc;border:1px solid #3a4250;pointer-events:none;display:flex;align-items:center;gap:10px;font-size:12px;color:#9ec9ff;text-shadow:0 1px 3px #000}
#nit .nb{flex:1;height:8px;border-radius:4px;background:#1c2230;overflow:hidden}
#nit i{display:block;height:100%;width:100%;background:linear-gradient(90deg,#2b7bff,#7cc4ff);box-shadow:0 0 10px #4aa3ff}
#nit.burn{border-color:#7cc4ff;box-shadow:0 0 16px #4aa3ff88;color:#fff}
#nit.burn i{background:linear-gradient(90deg,#7cc4ff,#fff);box-shadow:0 0 14px #bfe0ff}
#nit.spent{color:#6b7488}
#nit.spent i{background:#3a4250;box-shadow:none}
@media (max-width:760px){#nit{width:150px;top:118px}}
.pad button[data-k=nitro],#ced .eb[data-k=nitro]{border-color:#3aa0ff;color:#9ec9ff;background:#0e1c33}
.pad button.burn{background:#7cc4ff;color:#06203d;border-color:#fff;opacity:1}
.pad button.spent{opacity:calc(var(--po,.6)*.45)}
#start .edit{display:flex;""")

# ---------- HTML ----------
rep('<canvas id="gl"></canvas>','<canvas id="gl"></canvas>\n<canvas id="fx"></canvas>')
rep('<canvas id="mm"></canvas>','<canvas id="mm"></canvas>\n<div id="nit"><span>니트로</span><div class="nb"><i id="nbar"></i></div></div>')
rep('<div><button data-k="hand">드리프트</button><button data-k="brake">브레이크</button><button data-k="gas">가속</button></div>',
    '<div><button data-k="hand">드리프트</button><button data-k="brake">브레이크</button><button data-k="gas">가속</button><button data-k="nitro">니트로</button></div>')
rep('<button class="chip" data-k="hand" aria-pressed="false">드리프트</button>',
    '<button class="chip" data-k="hand" aria-pressed="false">드리프트</button>\n      <button class="chip" data-k="nitro" aria-pressed="false">니트로</button>')
rep('<button class="eb" data-k="gas">가속</button>\n</div>','<button class="eb" data-k="gas">가속</button><button class="eb" data-k="nitro">니트로</button>\n</div>')
rep('<li><span class="kk"><kbd>Space</kbd></span><em>핸드브레이크 (드리프트)</em></li>',
    '<li><span class="kk"><kbd>Space</kbd></span><em>핸드브레이크 (드리프트)</em></li>\n        <li><span class="kk"><kbd>N</kbd><kbd>Shift</kbd></span><em>니트로 (한 바퀴에 한 번)</em></li>')
rep('<li><span class="kk"><kbd>드리프트</kbd></span><em>핸드브레이크</em></li>',
    '<li><span class="kk"><kbd>드리프트</kbd></span><em>핸드브레이크</em></li>\n        <li><span class="kk"><kbd>니트로</kbd></span><em>한 바퀴에 한 번</em></li>')

# ---------- 상태·입력 ----------
rep("rpm=.2,gearI=0,started=false,dist=0,side=0;","rpm=.2,gearI=0,started=false,dist=0,side=0,NIT={ready:true,on:false,t:0},nitroK=0;")
rep("  c={x:sx,z:sz,h:sh,vx:0,vz:0};steer=0;ci=0;prog=0;lapStart=null;","  c={x:sx,z:sz,h:sh,vx:0,vz:0};steer=0;ci=0;prog=0;lapStart=null;NIT.ready=true;NIT.on=false;NIT.t=0;")
rep("const l=e.key.toLowerCase();if(l==='r')reset();","const l=e.key.toLowerCase();if((l==='n'||e.key==='Shift')&&!e.repeat){fireNitro();e.preventDefault()}if(l==='r')reset();")
rep("const k=b.dataset.k,set=v=>e=>{e.preventDefault();keys[k]=v;b.classList.toggle('on',!!v)};","const k=b.dataset.k,set=v=>e=>{e.preventDefault();keys[k]=v;b.classList.toggle('on',!!v);if(k==='nitro'&&v)fireNitro()};")

# ---------- 물리: 니트로 추가 가속 / 한 바퀴마다 1회 충전 ----------
rep("  if(keys.gas){vf+=13*Math.max(0,1-vf/80)*dt;if(lapStart===null)lapStart=performance.now()}",
    "  if(keys.gas){vf+=13*Math.max(0,1-vf/80)*dt;if(lapStart===null)lapStart=performance.now()}\n  if(NIT.on){vf+=22*clamp(vf/25,.35,1)*Math.max(0,1-vf/105)*dt;NIT.t-=dt;if(NIT.t<=0){NIT.on=false;NIT.t=0}}")
rep("  if(prog>=N){\n    prog-=N;","  if(prog>=N){\n    prog-=N;NIT.ready=true;")

# ---------- 소리 ----------
rep("let AC,eng,eg,ef,sg,t0a=0;","let AC,eng,eg,ef,sg,t0a=0,nzg,NBUF;")
rep("    t0a=AC.currentTime;ef=f;eg=g;sg=sk;eng=e;",
"""    NBUF=nb;const hp=AC.createBiquadFilter();hp.type='highpass';hp.frequency.value=2600;
    const zg=AC.createGain();zg.gain.value=0;const ns2=AC.createBufferSource();ns2.buffer=nb;ns2.loop=true;
    ns2.connect(hp);hp.connect(zg);zg.connect(AC.destination);ns2.start();nzg=zg;
    t0a=AC.currentTime;ef=f;eg=g;sg=sk;eng=e;""")
rep("  if(!keys.gas&&kmh<3)t=.2;else if(keys.gas&&kmh<10)t=Math.max(t,.7);","  if(!keys.gas&&kmh<3)t=.2;else if(keys.gas&&kmh<10)t=Math.max(t,.7);\n  if(NIT.on)t=Math.min(1,t+.12);\n  nitroK+=((NIT.on?1:0)-nitroK)*Math.min(1,dt*(NIT.on?6:3));if(nitroK<.002)nitroK=0;")
rep("eng.playbackRate.value=.3+.75*rpm;","eng.playbackRate.value=.3+.75*rpm+.12*nitroK;")
rep("eg.gain.value=(.25+.45*rpm*(keys.gas?1:.55))*clamp(","eg.gain.value=(.25+.45*rpm*(keys.gas?1:.55))*(1+.3*nitroK)*clamp(")
rep("    sg.gain.value=kmh>15?clamp((slip-4)/10,0,1)*.35:0;","    sg.gain.value=kmh>15?clamp((slip-4)/10,0,1)*.35:0;\n    if(nzg)nzg.gain.value=nitroK*.22;")
# HUD 갱신
rep("  $('cur').textContent=fmt(lapStart===null?0:performance.now()-lapStart);\n}",
"""  $('cur').textContent=fmt(lapStart===null?0:performance.now()-lapStart);
  $('nit').className=NIT.on?'burn':NIT.ready?'':'spent';
  $('nbar').style.width=(NIT.on?NIT.t/NIT_T*100:NIT.ready?100:0)+'%';
  nitBtn.classList.toggle('burn',NIT.on);nitBtn.classList.toggle('spent',!NIT.ready&&!NIT.on);
}""")

# ---------- 니트로 발동·효과 ----------
rep("/* ---------- 메인 루프 ---------- */","""/* ---------- 니트로: 한 바퀴에 한 번, 4초 동안 추가 가속 ---------- */
const NIT_T=4,nitBtn=document.querySelector('.pad button[data-k=nitro]');
function fireNitro(){
  if(!started||!NIT.ready||NIT.on)return;
  NIT.ready=false;NIT.on=true;NIT.t=NIT_T;
  if(lapStart===null)lapStart=performance.now();
  nitroBlast();
}
function nitroBlast(){
  if(!AC||!NBUF)return;
  const t=AC.currentTime,s=AC.createBufferSource();s.buffer=NBUF;
  const f=AC.createBiquadFilter();f.type='bandpass';f.Q.value=.9;
  f.frequency.setValueAtTime(2600,t);f.frequency.exponentialRampToValueAtTime(700,t+.5);
  const g=AC.createGain();g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.7,t+.03);g.gain.exponentialRampToValueAtTime(.001,t+.6);
  s.connect(f);f.connect(g);g.connect(AC.destination);s.start();s.stop(t+.7);
}
const fxc=$('fx'),fxg=fxc.getContext('2d');
const fxSize=()=>{fxc.width=innerWidth;fxc.height=innerHeight};
fxSize();addEventListener('resize',fxSize);
const streaks=Array.from({length:44},()=>({a:Math.random()*Math.PI*2,t:Math.random(),sp:.9+Math.random()*1.2,w:1+Math.random()*2}));
function drawFx(dt){
  fxg.clearRect(0,0,fxc.width,fxc.height);
  const k=nitroK;if(k<.01)return;
  const W=fxc.width,H=fxc.height,cx=W/2,cy=H*.4,R=Math.hypot(W,H)*.6;
  const g=fxg.createRadialGradient(cx,cy,Math.min(W,H)*.22,cx,cy,Math.max(W,H)*.78);
  g.addColorStop(0,'rgba(40,120,255,0)');g.addColorStop(1,'rgba(60,150,255,'+(.5*k).toFixed(3)+')');
  fxg.fillStyle=g;fxg.fillRect(0,0,W,H);fxg.lineCap='round';
  for(const s of streaks){
    s.t+=dt*s.sp*(.6+1.6*k);if(s.t>1){s.t=.08+Math.random()*.1;s.a=Math.random()*Math.PI*2}
    const t0=s.t,t1=Math.min(1.2,s.t+.05+.18*s.t),ca=Math.cos(s.a),sa=Math.sin(s.a);
    fxg.strokeStyle='rgba(200,230,255,'+(Math.min(1,s.t*1.3)*.55*k).toFixed(3)+')';
    fxg.lineWidth=s.w*(.6+s.t);
    fxg.beginPath();fxg.moveTo(cx+ca*R*t0*1.25,cy+sa*R*t0*.8);fxg.lineTo(cx+ca*R*t1*1.25,cy+sa*R*t1*.8);fxg.stroke();
  }
}

/* ---------- 메인 루프 ---------- */""")
rep("  sky.position.set(cam.position.x,SKY_Y,cam.position.z);",
"""  if(nitroK>0){cam.position.x+=(Math.random()-.5)*.035*nitroK;cam.position.y+=(Math.random()-.5)*.03*nitroK;cam.rotation.z+=(Math.random()-.5)*.006*nitroK}
  const fov=62+20*nitroK;if(Math.abs(cam.fov-fov)>.02){cam.fov=fov;cam.updateProjectionMatrix()}
  drawFx(dt);
  sky.position.set(cam.position.x,SKY_Y,cam.position.z);""")

# ---------- 버튼 배치: 니트로 추가 + 이전 저장본 이어받기 ----------
rep("K5=['left','right','hand','brake','gas'];","K5=['left','right','hand','brake','gas','nitro'];")
rep("""const okLay=L=>L&&K5.every(k=>L[k]&&isFinite(L[k].x)&&isFinite(L[k].y)&&L[k].s>=.5&&L[k].s<=2);
['L','P'].forEach(o=>{if(!okLay(CFG.lay[o]))CFG.lay[o]=null});""",
"""const okB=b=>b&&isFinite(b.x)&&isFinite(b.y)&&b.s>=.5&&b.s<=2;
['L','P'].forEach(o=>{
  const l=CFG.lay[o];
  if(!l||!K5.slice(0,5).every(k=>okB(l[k]))){CFG.lay[o]=null;return}
  /* 니트로 추가 전에 저장한 배치: 가속 버튼 위에 니트로를 붙여 줘요 */
  if(!okB(l.nitro)){const bh=PB[CFG.shape][1];l.nitro={x:l.gas.x,y:l.gas.y-(bh*l.gas.s/2+bh/2+8)/innerHeight,s:1}}
});""")
rep("  return L;\n}\nconst getLay=","  put('nitro',L.gas.x*W,L.gas.y*H-bh-g);\n  return L;\n}\nconst getLay=")
rep("    K5.forEach(k=>{l[k].x=1-l[k].x});\n    [['left','right'],['hand','gas']].forEach(([a,b])=>{const t=l[a].x;l[a].x=l[b].x;l[b].x=t});",
    "    K5.forEach(k=>{l[k].x=1-l[k].x});const gm=l.gas.x;\n    [['left','right'],['hand','gas']].forEach(([a,b])=>{const t=l[a].x;l[a].x=l[b].x;l[b].x=t});\n    l.nitro.x+=l.gas.x-gm;")

open('t_nitro.html','w',encoding='utf-8').write(h)
open('t.js','w',encoding='utf-8').write(re.findall(r'<script>(.*?)</script>',h,re.S)[-1])
print('built',len(h))
