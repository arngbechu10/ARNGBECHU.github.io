import re
h=open('t_home.html',encoding='utf-8').read()
def rep(a,b):
    global h
    assert h.count(a)==1,(h.count(a),a[:80]);h=h.replace(a,b)

# ---------- CSS: 게임 속 버튼을 저장된 위치·크기로 배치 ----------
i=h.index(".pad{position:fixed");j=h.index(":focus-visible{outline:2px solid #f2c230}")
PAD_CSS='''.pad{position:fixed;inset:0;z-index:5;display:none;pointer-events:none}
.pad div{display:contents}
.pad button{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:var(--bw,76px);height:var(--bh,76px);padding:0;white-space:nowrap;font-size:14px;opacity:var(--po,.6);pointer-events:auto;touch-action:none;user-select:none;-webkit-user-select:none}
body[data-pad=wide]{--bw:100px;--bh:54px}
body[data-pad=tall]{--bw:60px;--bh:112px}
body[data-pad=square]{--bw:76px;--bh:76px}
.pad button.on{background:#f2c230;color:#111;opacity:1}
@media (pointer:coarse){.pad{display:block}}
/* 조작 버튼 편집 화면 */
#ced{position:fixed;inset:0;z-index:70;display:none;background:#090a16;color:#eef;touch-action:none;user-select:none;-webkit-user-select:none;overflow:hidden}
#ced.on{display:block}
#ced .bg{position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,#090a16 0,#090a1600 45%),var(--sky) 50% 100%/auto 80% no-repeat,#090a16;opacity:.85}
#ced .grid{position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(#ffffff0f 1px,transparent 1px),linear-gradient(90deg,#ffffff0f 1px,transparent 1px);background-size:40px 40px}
#ced .eb{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:var(--bw,76px);height:var(--bh,76px);padding:0;white-space:nowrap;font-size:14px;border:2px solid #59627a;background:#1d2128;color:#eef;border-radius:8px;opacity:var(--po,.6);touch-action:none;cursor:grab}
#ced .eb:active{cursor:grabbing}
#ced .eb.sel{border-color:#f2c230;box-shadow:0 0 0 3px #f2c23066;opacity:1}
#ced .tb{position:absolute;left:50%;top:10px;transform:translateX(-50%);z-index:2;box-sizing:border-box;width:min(calc(100% - 20px),760px);display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;justify-content:center;padding:10px 14px;background:#0e1119f5;border:1px solid #2c3342;border-radius:14px}
#ced .chips{display:flex;gap:6px;flex-wrap:wrap}
#ced .chip{padding:6px 12px;border-radius:999px;background:#0b0d14;border:1.5px solid #2c3342;color:#9aa4b2;font-size:13px;cursor:pointer}
#ced .chip[aria-pressed=true]{border-color:#f2c230;color:#f2c230;background:#1a1810}
#ced .rg{display:flex;align-items:center;gap:8px;font-size:13px;color:#cdd7e6}
#ced .rg output{min-width:38px;text-align:right;font-variant-numeric:tabular-nums;color:#f2c230}
#ced input[type=range]{flex:none;width:130px;min-width:0;padding:0;border:0;background:none;accent-color:#f2c230}
#ced .acts{display:flex;gap:8px}
#ced .acts button{padding:8px 14px;font-size:14px;cursor:pointer}
#ced .acts .save{background:#f2c230;border-color:#f2c230;color:#111;font-weight:800}
#ced button:focus-visible,#ced input:focus-visible{outline:2px solid #fff;outline-offset:2px}
#start .edit{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;margin-top:10px;padding:10px;background:#141926;border:1.5px dashed #59627a;border-radius:10px;color:#eef;font-size:14px;cursor:pointer}
#start .edit:hover{border-color:#f2c230;color:#f2c230}
#start .edit:focus-visible{outline:2px solid #fff;outline-offset:2px}
'''
h=h[:i]+PAD_CSS+h[j:]

# ---------- HTML ----------
rep('''<button class="sw" id="swap" role="switch" aria-checked="false"><i></i><span>좌우 위치 바꾸기</span></button>''',
    '''<button class="sw" id="swap" role="switch" aria-checked="false"><i></i><span>좌우 위치 바꾸기</span></button>
      <button class="edit" id="editBtn"><span aria-hidden="true">✥</span>버튼 위치·크기 직접 조절</button>''')
rep('<script src="https://cdnjs','''<div id="ced" role="dialog" aria-label="조작 버튼 편집">
  <div class="bg"></div><div class="grid"></div>
  <div class="tb">
    <div class="chips" role="group" aria-label="편집할 버튼">
      <button class="chip" data-k="left" aria-pressed="false">◀</button>
      <button class="chip" data-k="right" aria-pressed="false">▶</button>
      <button class="chip" data-k="gas" aria-pressed="false">가속</button>
      <button class="chip" data-k="brake" aria-pressed="false">브레이크</button>
      <button class="chip" data-k="hand" aria-pressed="false">드리프트</button>
    </div>
    <label class="rg"><span>크기</span><input type="range" id="cedSize" min="50" max="200" step="5"><output id="cedSizeV">100%</output></label>
    <label class="rg"><span>투명도</span><input type="range" id="cedOp" min="20" max="100" step="5"><output id="cedOpV">60%</output></label>
    <div class="acts"><button id="cedReset">초기화</button><button id="cedCancel">취소</button><button class="save" id="cedSave">저장</button></div>
  </div>
  <button class="eb" data-k="left">◀</button><button class="eb" data-k="right">▶</button>
  <button class="eb" data-k="hand">드리프트</button><button class="eb" data-k="brake">브레이크</button><button class="eb" data-k="gas">가속</button>
</div>
<script src="https://cdnjs''')

# ---------- JS ----------
# --sky 변수는 홈과 편집 화면이 함께 쓰도록 문서 전체에 설정
rep("$('start').style.setProperty('--sky',","document.documentElement.style.setProperty('--sky',")
c=h.index("const PADS=['wide','tall','square'];");d=h.index("function showGuide")
NEW_JS=r'''const PADS=['wide','tall','square'],K5=['left','right','hand','brake','gas'];
const PB={wide:[100,54],tall:[60,112],square:[76,76]};
let CFG={shape:'square',swap:'0',opacity:.6,lay:{L:null,P:null}};
try{
  const j=JSON.parse(localStorage.getItem('drift-ctl2')||'null');
  if(j){CFG.shape=j.shape;CFG.swap=j.swap;CFG.opacity=j.opacity;CFG.lay={L:j.lay&&j.lay.L||null,P:j.lay&&j.lay.P||null}}
  else{CFG.shape=localStorage.getItem('drift-pad')||CFG.shape;CFG.swap=localStorage.getItem('drift-swap')||CFG.swap}
}catch(e){}
if(!PADS.includes(CFG.shape))CFG.shape='square';
if(CFG.swap!=='1')CFG.swap='0';
if(!(CFG.opacity>=.2&&CFG.opacity<=1))CFG.opacity=.6;
const okLay=L=>L&&K5.every(k=>L[k]&&isFinite(L[k].x)&&isFinite(L[k].y)&&L[k].s>=.5&&L[k].s<=2);
['L','P'].forEach(o=>{if(!okLay(CFG.lay[o]))CFG.lay[o]=null});
const saveCfg=()=>{try{localStorage.setItem('drift-ctl2',JSON.stringify(CFG))}catch(e){}};
const ori=()=>innerWidth>=innerHeight?'L':'P';
/* 기본 배치: 조향은 한쪽, 가속·브레이크·드리프트는 반대쪽 아래 모서리 */
function defaultLayout(shape,swap){
  const W=innerWidth,H=innerHeight,[bw,bh]=PB[shape],m=12,g=8,L={};
  const stack=bw*5+g*3+m*3>W,yb=H-m-bh/2,py=stack?yb-bh-g:yb;
  const put=(k,x,y)=>{L[k]={x:x/W,y:y/H,s:1}};
  if(swap==='1'){
    put('right',W-m-bw/2,yb);put('left',W-m-bw*1.5-g,yb);
    put('hand',m+bw/2,py);put('brake',m+bw*1.5+g,py);put('gas',m+bw*2.5+g*2,py);
  }else{
    put('left',m+bw/2,yb);put('right',m+bw*1.5+g,yb);
    put('gas',W-m-bw/2,py);put('brake',W-m-bw*1.5-g,py);put('hand',W-m-bw*2.5-g*2,py);
  }
  return L;
}
const getLay=o=>JSON.parse(JSON.stringify(CFG.lay[o]||defaultLayout(CFG.shape,CFG.swap)));
function clampPos(x,y,s){
  const [bw,bh]=PB[CFG.shape],hw=bw*s/2/innerWidth,hh=bh*s/2/innerHeight;
  return [clamp(x,hw,1-hw),clamp(y,hh,1-hh)];
}
function renderPad(){
  const L=getLay(ori());
  document.body.style.setProperty('--po',CFG.opacity);
  document.querySelectorAll('.pad button').forEach(b=>{
    const p=L[b.dataset.k],[x,y]=clampPos(p.x,p.y,p.s);
    b.style.left=(x*100)+'%';b.style.top=(y*100)+'%';b.style.transform='translate(-50%,-50%) scale('+p.s+')';
  });
}
function applyPad(){
  document.body.dataset.pad=CFG.shape;document.body.dataset.swap=CFG.swap;
  document.querySelectorAll('#start .shapes button').forEach(b=>{const on=b.dataset.shape===CFG.shape;b.setAttribute('aria-checked',on);b.tabIndex=on?0:-1});
  $('swap').setAttribute('aria-checked',CFG.swap==='1');
  renderPad();saveCfg();
}
document.querySelectorAll('#start .shapes button').forEach(b=>{
  b.onclick=()=>{CFG.shape=b.dataset.shape;applyPad()};
  b.onkeydown=e=>{
    const i=PADS.indexOf(CFG.shape);
    if(e.key==='ArrowRight'||e.key==='ArrowDown')CFG.shape=PADS[(i+1)%3];
    else if(e.key==='ArrowLeft'||e.key==='ArrowUp')CFG.shape=PADS[(i+2)%3];
    else return;
    e.preventDefault();applyPad();document.querySelector('#start .shapes [aria-checked=true]').focus();
  };
});
/* 좌우 위치 바꾸기: 직접 조절한 배치도 조향 쪽과 페달 쪽을 서로 맞바꿔요 */
$('swap').onclick=()=>{
  CFG.swap=CFG.swap==='1'?'0':'1';
  ['L','P'].forEach(o=>{
    const l=CFG.lay[o];if(!l)return;
    K5.forEach(k=>{l[k].x=1-l[k].x});
    [['left','right'],['hand','gas']].forEach(([a,b])=>{const t=l[a].x;l[a].x=l[b].x;l[b].x=t});
  });
  applyPad();
};
applyPad();addEventListener('resize',renderPad);

/* ---------- 조작 버튼 편집: 끌어서 옮기고, 슬라이더로 크기·투명도 ---------- */
let draft=null,sel='gas',edOp=.6,drag=null;
const edBtns=[...document.querySelectorAll('#ced .eb')];
function renderEd(){
  edBtns.forEach(b=>{
    const k=b.dataset.k,p=draft[k];[p.x,p.y]=clampPos(p.x,p.y,p.s);
    b.style.left=(p.x*100)+'%';b.style.top=(p.y*100)+'%';b.style.transform='translate(-50%,-50%) scale('+p.s+')';
    b.classList.toggle('sel',k===sel);
  });
  document.querySelectorAll('#ced .chip').forEach(c=>c.setAttribute('aria-pressed',c.dataset.k===sel));
  const sz=Math.round(draft[sel].s*100),op=Math.round(edOp*100);
  $('cedSize').value=sz;$('cedSizeV').textContent=sz+'%';
  $('cedOp').value=op;$('cedOpV').textContent=op+'%';
  document.body.style.setProperty('--po',edOp);
}
function openEditor(){
  draft=getLay(ori());edOp=CFG.opacity;sel='gas';drag=null;
  $('ced').classList.add('on');renderEd();$('cedSave').focus({preventScroll:true});
}
function closeEditor(){
  $('ced').classList.remove('on');draft=null;drag=null;
  document.body.style.setProperty('--po',CFG.opacity);
}
$('editBtn').onclick=openEditor;
$('cedCancel').onclick=closeEditor;
$('cedSave').onclick=()=>{CFG.lay[ori()]=draft;CFG.opacity=edOp;closeEditor();applyPad()};
$('cedReset').onclick=()=>{draft=defaultLayout(CFG.shape,CFG.swap);edOp=.6;renderEd()};
document.querySelectorAll('#ced .chip').forEach(c=>{c.onclick=()=>{sel=c.dataset.k;renderEd()}});
$('cedSize').oninput=e=>{draft[sel].s=e.target.value/100;renderEd()};
$('cedOp').oninput=e=>{edOp=e.target.value/100;renderEd()};
edBtns.forEach(b=>{
  b.addEventListener('pointerdown',e=>{
    e.preventDefault();sel=b.dataset.k;
    try{b.setPointerCapture(e.pointerId)}catch(_){}
    const p=draft[sel];
    drag={id:e.pointerId,k:sel,dx:e.clientX-p.x*innerWidth,dy:e.clientY-p.y*innerHeight};
    renderEd();
  });
  b.addEventListener('pointermove',e=>{
    if(!drag||drag.id!==e.pointerId)return;
    const p=draft[drag.k];
    [p.x,p.y]=clampPos((e.clientX-drag.dx)/innerWidth,(e.clientY-drag.dy)/innerHeight,p.s);
    renderEd();
  });
  ['pointerup','pointercancel'].forEach(t=>b.addEventListener(t,e=>{if(drag&&drag.id===e.pointerId)drag=null}));
});
/* 키보드: 방향키로 미세 이동(Shift는 크게), +/-는 크기, Esc는 취소 */
addEventListener('keydown',e=>{
  if(!draft||!$('ced').classList.contains('on'))return;
  const p=draft[sel],st=e.shiftKey?.05:.01;
  if(e.key==='Escape'){closeEditor();e.preventDefault();return}
  if(e.target.matches&&e.target.matches('input[type=range]'))return;
  if(e.key==='ArrowLeft')p.x-=st;else if(e.key==='ArrowRight')p.x+=st;
  else if(e.key==='ArrowUp')p.y-=st;else if(e.key==='ArrowDown')p.y+=st;
  else if(e.key==='+'||e.key==='=')p.s=clamp(p.s+.05,.5,2);
  else if(e.key==='-')p.s=clamp(p.s-.05,.5,2);
  else return;
  e.preventDefault();renderEd();
});
'''
h=h[:c]+NEW_JS+h[d:]
open('t_edit.html','w',encoding='utf-8').write(h)
open('t.js','w',encoding='utf-8').write(re.findall(r'<script>(.*?)</script>',h,re.S)[-1])
print('built',len(h))
