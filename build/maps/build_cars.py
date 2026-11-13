import re, base64, json
W='/tmp/claude-0/-home-claude/f9ae0b19-9e15-514d-b64c-42a1ff34b6c5/scratchpad/'
h=open(W+'w/t_maps.html',encoding='utf-8').read()
RB=W+'rb/'
b64=lambda p:'data:image/webp;base64,'+base64.b64encode(open(RB+p,'rb').read()).decode()
cfg=json.load(open(RB+'wheelcfg.json'))

def rep1(old,new,cnt=1):
    global h
    assert h.count(old)==cnt,(old[:80],h.count(old))
    h=h.replace(old,new)

# ---------- CSS ----------
rep1("#start .car{position:relative;display:block;width:auto;height:auto;max-width:100%;max-height:min(40vh,calc(100vh - 330px));",
     "#start .car{position:relative;display:block;width:auto;height:auto;max-width:100%;max-height:var(--cmh);")
rep1("#start .carwrap{position:relative;width:100%;display:flex;justify-content:center}",
     "#start .carwrap{position:relative;width:100%;display:flex;justify-content:center;align-items:flex-end;height:var(--cmh)}")
rep1("#start{--gold:#f2c230;","#start{--cmh:max(110px,min(34vh,calc(100vh - 430px)));--gold:#f2c230;")
rep1("  #start .car{max-height:30vh}\n","  #start{--cmh:30vh}\n")
rep1("  #start .car{max-height:40vh}#start .keys{gap:6px}","  #start{--cmh:max(84px,22vh)}#start .cname{display:none}#start .keys{gap:6px}")
rep1("#start .maps{","""#start .cname{font-size:clamp(12px,1.9vh,14px);color:#cdd7e6;letter-spacing:.04em;margin-top:calc(-1*clamp(6px,2vh,18px));text-align:center;min-height:1.2em}
#start .cars{display:flex;gap:8px;width:min(100%,620px);padding:0 10px;box-sizing:border-box}
#start .cars button{flex:1;min-width:0;padding:6px 4px 5px;background:#0b0d14;border:2px solid var(--line);border-radius:10px;color:#8d96a3;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:3px;transition:border-color .12s,color .12s,transform .12s}
#start .cars button:hover{transform:translateY(-2px)}
#start .cars img,#start .cars svg{display:block;width:100%;height:clamp(28px,5.6vh,48px);object-fit:contain;opacity:.75;transition:opacity .15s}
#start .cars span{font-size:11px;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
#start .cars button[aria-checked=true]{border-color:var(--gold);color:#fff;background:#1a1810}
#start .cars button[aria-checked=true] img{opacity:1}
#start .cars button.locked img,#start .cars button.locked svg{opacity:.5;filter:grayscale(1)}
#start .cars button.shake{animation:shk .38s}
@keyframes shk{20%{transform:translateX(-5px)}40%{transform:translateX(5px)}60%{transform:translateX(-3px)}80%{transform:translateX(3px)}}
#start .cars button:focus-visible{outline:3px solid #fff;outline-offset:2px}
#toast{position:fixed;left:50%;top:18px;transform:translate(-50%,-8px);z-index:80;max-width:90vw;box-sizing:border-box;background:#2a1216f2;border:1px solid #ff6b5e;color:#ffd7d2;padding:11px 18px;border-radius:10px;font-weight:700;font-size:15px;opacity:0;pointer-events:none;transition:opacity .2s,transform .2s;text-align:center}
#toast.on{opacity:1;transform:translate(-50%,0)}
@media (max-height:520px){#start .cars span{display:none}#start .cars button{padding:4px}#start .cars img,#start .cars svg{height:26px}}
#start .maps{""")

# ---------- HTML ----------
tesla_svg='<img alt="" src="'+b64('tesla.webp')+'">'
rep1('''    <div class="maps" role="radiogroup" aria-label="맵 선택">''','''    <div class="cname" id="cname"></div>
    <div class="cars" role="radiogroup" aria-label="차량 선택">
      <button role="radio" aria-checked="true" data-car="gtr"><img alt=""><span>GT-R R34</span></button>
      <button role="radio" aria-checked="false" data-car="gt3"><img alt=""><span>911 GT3 RS</span></button>
      <button role="radio" aria-checked="false" data-car="chal"><img alt=""><span>Challenger</span></button>
      <button role="radio" aria-checked="false" data-car="f40"><img alt=""><span>F40</span></button>
      <button role="radio" aria-checked="false" data-car="mcl"><img alt=""><span>720S</span></button>
      <button role="radio" aria-checked="false" aria-disabled="true" class="locked" data-car="tesla">%TESLA%<span>Tesla Roadster</span></button>
    </div>
    <div class="maps" role="radiogroup" aria-label="맵 선택">'''.replace('%TESLA%',tesla_svg))
rep1("<div id=\"ced\" role=\"dialog\"",'<div id="toast" role="alert" aria-live="assertive"></div>\n<div id="ced" role="dialog"')

# ---------- JS ----------
js=r"""
/* ---------- 차량 선택 ---------- */
const GTR={hero:document.querySelector('#start .car').src,cabin:$('cabin').src,wheel:$('wheel').src};
const CARS={
  gtr:{name:'Nissan Skyline GT-R R34',hero:GTR.hero,cabin:GTR.cabin,wheel:GTR.wheel,wx:69.5,wy:88,ww:20,gx:31.4,gy:77.3,engine:null,launch:null},
  gt3:{name:'Porsche 911 GT3 RS',hero:'%H1%',cabin:'%C1%',wheel:'%W1%',wx:%GX1%,wy:%GY1%,ww:%GW1%,gx:71,gy:77.3,engine:'%E1%',launch:'%L1%'},
  chal:{name:'Dodge Challenger SRT',hero:'%H2%',cabin:'%C2%',wheel:'%W2%',wx:%GX2%,wy:%GY2%,ww:%GW2%,gx:71,gy:77.3,engine:'%E2%',launch:'%L2%'},
  f40:{name:'Ferrari F40',hero:'%H3%',cabin:'%C3%',wheel:'%W3%',wx:%GX3%,wy:%GY3%,ww:%GW3%,gx:71,gy:77.3,engine:'%E3%',launch:'%L3%'},
  mcl:{name:'McLaren 720S',hero:'%H4%',cabin:'%C4%',wheel:'%W4%',wx:%GX4%,wy:%GY4%,ww:%GW4%,gx:71,gy:77.3,engine:'%E4%',launch:'%L4%'}
};
let CARID='gtr';
const carImg=document.querySelector('#start .car');
document.querySelectorAll('.cars button[data-car]').forEach(b=>{const C=CARS[b.dataset.car],i=b.querySelector('img');if(C&&i)i.src=C.hero});
function setCar(id,anim){
  const C=CARS[id];if(!C)return;CARID=id;
  $('cabin').src=C.cabin;$('wheel').src=C.wheel;
  const w=$('wheel').style;w.left=C.wx+'%';w.top=C.wy+'%';w.width=C.ww+'%';
  $('gg').style.left=C.gx+'%';$('gg').style.top=C.gy+'%';
  carImg.src=C.hero;$('cname').textContent=C.name;
  if(anim){carImg.style.animation='none';void carImg.offsetWidth;carImg.style.animation=''}
  document.querySelectorAll('.cars button').forEach(b=>b.setAttribute('aria-checked',b.dataset.car===id));
  try{localStorage.setItem('drift-car',id)}catch(e){}
}
let toastT=0;
function toast(msg){const t=$('toast');t.textContent=msg;t.classList.add('on');clearTimeout(toastT);toastT=setTimeout(()=>t.classList.remove('on'),2600)}
document.querySelectorAll('.cars button').forEach(b=>b.onclick=()=>{
  const id=b.dataset.car;
  if(!CARS[id]){toast('이딴건 차가 아닙니다 사용하실 수 없습니다');b.classList.remove('shake');void b.offsetWidth;b.classList.add('shake');return}
  if(id!==CARID)setCar(id,true);
});
let _c0='gtr';try{_c0=localStorage.getItem('drift-car')||'gtr'}catch(e){}
setCar(CARS[_c0]?_c0:'gtr');
"""
for i,(k,hero) in enumerate([('gt3','hero_gt3.webp'),('chal','hero_chal.webp'),('f40','hero_f40.webp'),('mcl','hero_mcl.webp')],1):
    js=js.replace('%H%d%%'%0,'') if False else js
    js=js.replace('%%H%d%%'%i,b64(hero)).replace('%%C%d%%'%i,b64('cabin_%s.webp'%k)).replace('%%W%d%%'%i,b64('wheelS_%s.webp'%k))
    wav=lambda f:'data:audio/wav;base64,'+base64.b64encode(open(RB+f,'rb').read()).decode()
    js=js.replace('%%E%d%%'%i,wav('eng_%s.wav'%k)).replace('%%L%d%%'%i,wav('lau_%s.wav'%k))
    js=js.replace('%%GX%d%%'%i,str(cfg[k]['wx'])).replace('%%GY%d%%'%i,str(cfg[k]['wy'])).replace('%%GW%d%%'%i,str(cfg[k]['ww']))
rep1("\n$('go').onclick=()=>{",js+"\n$('go').onclick=()=>{")
# 미끄럼(타이어) 소리: 드리프트(핸드브레이크)를 누르고 있을 때만
rep1("sg.gain.value=kmh>15?clamp((slip-4)/10,0,1)*.35:0;","skG+=((keys.hand&&kmh>15?clamp((slip-3)/9,0,1)*.35:0)-skG)*Math.min(1,dt*12);sg.gain.value=skG;")
rep1("let needle=0;","let needle=0,skG=0;")
# 소리: 차량별 파일이 생기면 자동으로 사용 (없으면 GT-R 소리)
rep1("[ENG,LAU].map(u=>AC.decodeAudioData(b64buf(u)))","[CARS[CARID].engine||ENG,CARS[CARID].launch||LAU].map(u=>AC.decodeAudioData(b64buf(u)))")
open(W+'w/t_cars.html','w',encoding='utf-8').write(h)
print('built',len(h))
