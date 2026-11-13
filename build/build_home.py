import re,base64
h=open('t_gauge2.html',encoding='utf-8').read()
car='data:image/webp;base64,'+base64.b64encode(open('car.webp','rb').read()).decode()
def rep(a,b,cnt=1):
    global h
    assert h.count(a)==cnt,(h.count(a),a[:80]);h=h.replace(a,b)

# ---------- CSS ----------
i=h.index("#start{position:fixed");j=h.index(".pad{position:fixed")
old_css=h[i:j]
assert "#go{" in old_css
HOME_CSS=r'''#start{--gold:#f2c230;--line:#2c3342;--u:8px;position:fixed;inset:0;z-index:50;display:grid;grid-template-columns:minmax(0,1.2fr) minmax(310px,.8fr);grid-template-rows:minmax(0,1fr);gap:clamp(12px,3vw,44px);padding:clamp(12px,3.5vh,36px) clamp(14px,3.5vw,48px);background:#090a16;overflow:hidden;text-align:left;color:#eef}
#start .bg{position:absolute;inset:0;pointer-events:none;background:radial-gradient(70% 55% at 30% 80%,#2f62ff3a,transparent 70%),linear-gradient(90deg,#090a1688 0,#090a1600 40%,#090a16f0 100%),linear-gradient(0deg,#090a16 0,#090a1600 36%),var(--sky) 50% 100%/auto 80% no-repeat,#090a16}
#start .hero{position:relative;z-index:1;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:clamp(16px,5vh,44px);min-width:0;min-height:0}
#start .carwrap{position:relative;width:100%;display:flex;justify-content:center}
#start .carwrap::before{content:"";position:absolute;left:50%;bottom:-7%;width:86%;height:24%;transform:translateX(-50%);background:radial-gradient(closest-side,#3a6bffa0,#3a6bff00);filter:blur(12px)}
#start .carwrap::after{content:"";position:absolute;left:4%;right:4%;bottom:-3%;height:2px;background:linear-gradient(90deg,transparent,#ffffff66,transparent)}
#start .car{position:relative;display:block;width:auto;height:auto;max-width:100%;max-height:46vh;filter:drop-shadow(0 16px 22px #000c);animation:drive-in .95s cubic-bezier(.16,.84,.3,1) both}
@keyframes drive-in{from{opacity:0;transform:translateX(-10%)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){#start .car{animation:none}}
#start .cta{display:flex;gap:16px;width:min(100%,540px);padding:0 10px;box-sizing:border-box}
#start .btn{font:inherit;height:clamp(48px,8vh,60px);padding:0 12px;border:2px solid transparent;border-radius:6px;cursor:pointer;transform:skewX(-12deg);transition:transform .12s,filter .12s;color:#101218}
#start .btn span{display:inline-block;transform:skewX(12deg);font-weight:800;font-size:clamp(16px,2.6vh,21px);letter-spacing:.04em}
#start .play{flex:1.5;background:var(--gold);border-color:var(--gold);box-shadow:0 0 28px #f2c23055}
#start .ghost{flex:1;background:#10131c;border-color:#59627a;color:#eef}
#start .btn:hover{transform:skewX(-12deg) translateY(-2px);filter:brightness(1.1)}
#start .btn:active{transform:skewX(-12deg) scale(.97)}
#start .btn:focus-visible{outline:3px solid #fff;outline-offset:3px}
#start .panel{box-sizing:border-box;position:relative;z-index:1;align-self:center;max-height:calc(100vh - 2*clamp(12px,3.5vh,36px));max-height:calc(100dvh - 2*clamp(12px,3.5vh,36px));overflow:auto;overscroll-behavior:contain;scrollbar-width:thin;background:#0e1119f0;border:1px solid var(--line);border-radius:16px;padding:clamp(14px,2.6vh,22px);display:flex;flex-direction:column;gap:clamp(14px,2.6vh,24px)}
#start h2{margin:0 0 10px;font-size:15px;font-weight:700;color:#dbe2ee}
#start .shapes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
#start .shapes button{display:flex;flex-direction:column;align-items:center;gap:9px;padding:12px 4px 10px;background:#0b0d14;border:1.5px solid var(--line);border-radius:10px;color:#8d96a3;font-size:13px;cursor:pointer;transition:border-color .12s,color .12s,background .12s}
#start .shapes button[aria-checked=true]{border-color:var(--gold);color:var(--gold);background:#1a1810}
#start .shapes button:focus-visible,#start .sw:focus-visible,#start .tabs button:focus-visible{outline:2px solid #fff;outline-offset:2px}
#start .pv{display:flex;justify-content:center;align-items:flex-end;gap:calc(.8*var(--u));height:calc(2.4*var(--u))}
#start .pv i{display:flex;gap:calc(.25*var(--u));align-items:flex-end}
#start .pv b{display:block;background:currentColor;border-radius:2px;opacity:.92}
#start [data-shape=wide] .pv b{width:calc(2.2*var(--u));height:calc(1.2*var(--u))}
#start [data-shape=tall] .pv b{width:calc(1.15*var(--u));height:calc(2.3*var(--u))}
#start [data-shape=square] .pv b{width:calc(1.6*var(--u));height:calc(1.6*var(--u))}
body[data-swap="1"] #start .pv{flex-direction:row-reverse}
#start .sw{display:flex;align-items:center;gap:10px;margin-top:10px;padding:6px 2px;background:none;border:0;color:#cdd7e6;font-size:14px;cursor:pointer}
#start .sw i{flex:none;width:38px;height:22px;border-radius:11px;background:#2c3342;position:relative;transition:background .15s}
#start .sw i::after{content:"";position:absolute;top:3px;left:3px;width:16px;height:16px;border-radius:50%;background:#cdd7e6;transition:transform .15s,background .15s}
#start .sw[aria-checked=true] i{background:var(--gold)}
#start .sw[aria-checked=true] i::after{transform:translateX(16px);background:#111}
#start .tabs{display:inline-flex;background:#0a0c13;border:1px solid var(--line);border-radius:10px;padding:3px;margin-bottom:12px}
#start .tabs button{background:none;border:0;color:#9aa4b2;padding:7px 18px;border-radius:7px;font-size:14px;cursor:pointer}
#start .tabs button[aria-selected=true]{background:#252b3a;color:#fff}
#start .keys{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:9px}
#start .keys[hidden]{display:none}
#start .keys li{display:flex;align-items:center;gap:14px}
#start .kk{display:flex;gap:4px;min-width:136px;flex:none}
#start kbd{display:inline-flex;align-items:center;justify-content:center;min-width:28px;height:28px;padding:0 7px;box-sizing:border-box;border:1px solid #3a4250;border-bottom-width:3px;border-radius:6px;background:#1a1f2b;color:#eef;font:600 13px/1 system-ui,sans-serif}
#start .keys em{font-style:normal;color:#cdd7e6;font-size:14px}
@media (max-width:900px){#start{--u:5.5px}}
@media (max-aspect-ratio:1/1),(max-width:760px){
  #start{grid-template-columns:1fr;grid-template-rows:auto auto;align-content:start;overflow-y:auto}
  #start .car{max-height:30vh}
  #start .panel{max-height:none;overflow:visible;align-self:stretch}
}
@media (max-height:480px) and (orientation:landscape){
  #start .car{max-height:40vh}#start .keys{gap:6px}#start kbd{height:24px;font-size:12px}
  #start .shapes button{padding:8px 4px 7px;gap:6px}
}
'''
h=h[:i]+HOME_CSS+h[j:]

# 화면 조작 버튼: 모양/좌우 위치 설정 반영
rep(".pad button{min-width:68px;min-height:60px;opacity:.6;pointer-events:auto;touch-action:none}",
""".pad{flex-wrap:wrap-reverse;gap:8px}
.pad button{width:var(--bw,76px);height:var(--bh,76px);padding:0;white-space:nowrap;font-size:14px;opacity:.6;pointer-events:auto;touch-action:none}
body[data-pad=wide]{--bw:100px;--bh:54px}
body[data-pad=tall]{--bw:60px;--bh:112px}
body[data-pad=square]{--bw:76px;--bh:76px}
body[data-swap="1"] .pad{flex-direction:row-reverse}""")

# ---------- HTML ----------
a=h.index('<div id="start">');b=h.index('<script src="https://cdnjs')
pv=lambda s,n:'<button role="radio" aria-checked="false" data-shape="%s"><span class="pv"><i><b></b><b></b></i><i><b></b><b></b><b></b></i></span><span>%s</span></button>'%(s,n)
HOME_HTML='''<div id="start">
  <div class="bg"></div>
  <div class="hero">
    <div class="carwrap"><img class="car" src="'''+car+'''" alt=""></div>
    <div class="cta">
      <button class="btn play" id="go"><span>플레이</span></button>
      <button class="btn ghost" id="lbBtn"><span>리더보드</span></button>
    </div>
  </div>
  <section class="panel" aria-label="조작 설정">
    <div>
      <h2>방향키 조작</h2>
      <div class="shapes" role="radiogroup" aria-label="방향키 모양">
        '''+pv('wide','가로형')+'''
        '''+pv('tall','세로형')+'''
        '''+pv('square','정사각형')+'''
      </div>
      <button class="sw" id="swap" role="switch" aria-checked="false"><i></i><span>좌우 위치 바꾸기</span></button>
    </div>
    <div>
      <h2>조작법</h2>
      <div class="tabs" role="tablist" aria-label="기기 선택">
        <button role="tab" id="tPc" aria-selected="true">컴퓨터</button>
        <button role="tab" id="tMo" aria-selected="false">모바일</button>
      </div>
      <ul class="keys" id="gPc">
        <li><span class="kk"><kbd>↑</kbd><kbd>W</kbd></span><em>가속</em></li>
        <li><span class="kk"><kbd>↓</kbd><kbd>S</kbd></span><em>브레이크</em></li>
        <li><span class="kk"><kbd>←</kbd><kbd>→</kbd><kbd>A</kbd><kbd>D</kbd></span><em>핸들 좌우</em></li>
        <li><span class="kk"><kbd>Space</kbd></span><em>핸드브레이크 (드리프트)</em></li>
        <li><span class="kk"><kbd>R</kbd></span><em>처음부터 다시</em></li>
        <li><span class="kk"><kbd>L</kbd></span><em>순위표 열기</em></li>
      </ul>
      <ul class="keys" id="gMo" hidden>
        <li><span class="kk"><kbd>◀</kbd><kbd>▶</kbd></span><em>핸들 좌우</em></li>
        <li><span class="kk"><kbd>가속</kbd></span><em>누르는 동안 가속</em></li>
        <li><span class="kk"><kbd>브레이크</kbd></span><em>감속과 정지</em></li>
        <li><span class="kk"><kbd>드리프트</kbd></span><em>핸드브레이크</em></li>
      </ul>
    </div>
  </section>
</div>
'''
h=h[:a]+HOME_HTML+h[b:]

# ---------- JS ----------
# 하늘 이미지를 홈 배경에서도 재사용
m=re.search(r"const skyT=rep\(TL\.load\('(data:image/webp;base64,[^']+)'\)\);",h);assert m
h=h.replace(m.group(0),"const SKY_URI='"+m.group(1)+"';\n$('start').style.setProperty('--sky','url(\"'+SKY_URI+'\")');\nconst skyT=rep(TL.load(SKY_URI));")
# 홈에서는 게임 키 입력을 받지 않음, 홈에서는 3D 렌더링 중단
rep("  if(e.target.tagName==='INPUT')return;\n","  if(e.target.tagName==='INPUT'||!started)return;\n")
rep("  R.render(S,cam);\n}","  if(started)R.render(S,cam);\n}")
# 홈 설정 로직
rep("$('go').onclick=","""/* ---------- 홈: 방향키 모양·위치, 조작법 탭, 리더보드 버튼 ---------- */
const PADS=['wide','tall','square'];
let padShape='square',padSwap='0';
try{padShape=localStorage.getItem('drift-pad')||padShape;padSwap=localStorage.getItem('drift-swap')||padSwap}catch(e){}
if(!PADS.includes(padShape))padShape='square';
if(padSwap!=='1')padSwap='0';
function applyPad(){
  document.body.dataset.pad=padShape;document.body.dataset.swap=padSwap;
  document.querySelectorAll('#start .shapes button').forEach(b=>{const on=b.dataset.shape===padShape;b.setAttribute('aria-checked',on);b.tabIndex=on?0:-1});
  $('swap').setAttribute('aria-checked',padSwap==='1');
  try{localStorage.setItem('drift-pad',padShape);localStorage.setItem('drift-swap',padSwap)}catch(e){}
}
document.querySelectorAll('#start .shapes button').forEach(b=>{
  b.onclick=()=>{padShape=b.dataset.shape;applyPad()};
  b.onkeydown=e=>{
    const i=PADS.indexOf(padShape);
    if(e.key==='ArrowRight'||e.key==='ArrowDown')padShape=PADS[(i+1)%3];
    else if(e.key==='ArrowLeft'||e.key==='ArrowUp')padShape=PADS[(i+2)%3];
    else return;
    e.preventDefault();applyPad();document.querySelector('#start .shapes [aria-checked=true]').focus();
  };
});
$('swap').onclick=()=>{padSwap=padSwap==='1'?'0':'1';applyPad()};
applyPad();
function showGuide(mo){
  $('tPc').setAttribute('aria-selected',!mo);$('tMo').setAttribute('aria-selected',mo);
  $('gPc').hidden=mo;$('gMo').hidden=!mo;
}
$('tPc').onclick=()=>showGuide(false);$('tMo').onclick=()=>showGuide(true);
showGuide(matchMedia('(pointer:coarse)').matches);
/* 리더보드 버튼: 아직 연결하지 않았어요. 연결할 때 이 함수만 채우면 돼요. */
function openLeaderboard(){}
$('lbBtn').onclick=()=>openLeaderboard();

$('go').onclick=""")
open('t_home.html','w',encoding='utf-8').write(h)
open('t.js','w',encoding='utf-8').write(re.findall(r'<script>(.*?)</script>',h,re.S)[-1])
print('built',len(h))
