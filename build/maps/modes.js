/* ---------- 리더보드 (Supabase) ---------- */
const SB='https://payqqpkkdpydypinyptz.supabase.co/rest/v1/scores';
const KEY='sb_publishable_HLjviD6kti7QDGOQ0mlMgQ_qoPBcKh6';
const HDR={apikey:KEY,'Content-Type':'application/json'};
/* RICH: scores 표에 map / mode / stage 열이 있으면 true, 없으면 false (처음엔 모름) */
var RICH=null;
var MODE='lap',HOLD=false,DEAD=false,PLAYER='';
const MAPLABEL={seoul:'Seoul',mountain:'Mountain Pass',xmas:'Christmas',ship:'Cargo Ship'};
const HARD_STAGES=['xmas','seoul','mountain','ship']; /* 쉬운 순서. 새 맵은 이 배열 뒤에 이름만 추가하면 다음 스테이지가 돼요 */
const HARD_HITS=5;                              /* 벽에 이 횟수만큼 박으면 폭발 */
const HARD_RESET_PER_STAGE=false;               /* true면 스테이지마다 충돌 횟수를 새로 셉니다 */
function boardUrl(){
  if(RICH===false)return SB+'?select=name,lap_ms&order=lap_ms.asc&limit=200';
  if(MODE==='hard')return SB+'?select=name,lap_ms,stage&mode=eq.hard&order=stage.desc,lap_ms.asc&limit=200';
  return SB+'?select=name,lap_ms&mode=eq.lap&map=eq.'+MAPID+'&order=lap_ms.asc&limit=200';
}
async function loadBoard(){
  const ol=$('lb');
  $('lbTitle').textContent=MODE==='hard'?'하드 리더보드':'리더보드 · '+(MAPLABEL[MAPID]||MAPID);
  const one=txt=>{ol.textContent='';const li=document.createElement('li');li.textContent=txt;ol.append(li)};
  if(RICH===false&&(MODE==='hard'||MAPID!=='seoul'))return one('이 순위표는 아직 준비 중이에요.');
  try{
    const r=await fetch(boardUrl(),{headers:HDR});
    if(!r.ok){if(RICH===null&&r.status===400){RICH=false;return loadBoard()}throw new Error(r.status)}
    if(RICH===null)RICH=true;
    const rows=await r.json(),seen=new Set(),top=[];
    for(const x of rows){const k=x.name.trim().toLowerCase();if(seen.has(k))continue;seen.add(k);top.push(x);if(top.length==10)break}
    if(!top.length)return one('아직 기록이 없어요. 첫 기록을 올려보세요.');
    ol.textContent='';
    top.forEach((x,i)=>{const li=document.createElement('li');
      li.innerHTML='<span class="n"></span><span class="m"></span><span class="t"></span>';
      li.children[0].textContent=i+1;li.children[1].textContent=x.name;
      li.children[2].textContent=(MODE==='hard'&&RICH?'S'+x.stage+' · ':'')+fmt(x.lap_ms);ol.append(li)});
  }catch(e){one('리더보드를 불러오지 못했어요. 새로고침해 주세요.')}
}
/* 기록 올리기. 'ok' 올림 / 'pending' 이 순위표는 아직 준비 중 / 실패하면 throw */
async function sendScore(p){
  if(RICH!==false){
    const r=await fetch(SB,{method:'POST',headers:{...HDR,Prefer:'return=minimal'},body:JSON.stringify(p)});
    if(r.ok){RICH=true;return 'ok'}
    if(r.status===400||r.status===404)RICH=false;else throw new Error(r.status);
  }
  if(p.mode==='lap'&&p.map==='seoul'){
    const r=await fetch(SB,{method:'POST',headers:{...HDR,Prefer:'return=minimal'},body:JSON.stringify({name:p.name,lap_ms:p.lap_ms})});
    if(!r.ok)throw new Error(r.status);return 'ok';
  }
  return 'pending';
}
try{PLAYER=(localStorage.getItem('drift-name')||'').slice(0,20)}catch(e){}
$('name').value=PLAYER;
async function doSend(){
  const name=($('name').value||PLAYER).trim().slice(0,20);
  if(!name){$('msg').textContent='이름을 먼저 입력해 주세요.';return}
  if(bestLap===null||MODE==='hard')return;
  const ms=bestLap,mp=MAPID;
  $('send').disabled=true;$('msg').textContent='올리는 중...';
  try{
    const res=await sendScore({name,lap_ms:ms,map:mp,mode:'lap'});
    if(res==='ok'){$('msg').textContent=fmt(ms)+' 기록을 올렸어요.';loadBoard()}
    else $('msg').textContent='새 기록이에요! (이 맵 순위표는 아직 준비 중이에요)';
  }catch(e){$('msg').textContent='올리지 못했어요. 잠시 후 다시 눌러주세요.';$('send').disabled=false}
}
const autoSend=()=>{if(PLAYER||$('name').value.trim())doSend()};
$('send').onclick=doSend;

/* ---------- 모드 선택 → 이름 입력 → 홈 ---------- */
const MODENAME={lap:'개인 랩타임',hard:'하드 랩타임'};
const MC=document.querySelectorAll('#modes .mc');
let hardIdx=0,hits=0,stageTimes=[],lastHit=0,failT=0;
function stopAudio(){if(AC){try{AC.close()}catch(e){}}AC=null;eng=null;sg=null;eg=null;nzg=null}
function showModes(){
  stopAudio();started=false;DEAD=false;HOLD=false;
  ['hh','boom','fail','stg','hit'].forEach(i=>$(i).classList.remove('on','win'));
  $('lbp').classList.remove('on','top');
  $('start').style.display='none';$('modes').classList.add('on');
  $('mStep1').hidden=false;$('mStep2').hidden=true;
  document.body.removeAttribute('data-mode');
}
function applyMode(){
  document.body.dataset.mode=MODE;
  $('mbMode').textContent=MODENAME[MODE];$('mbName').textContent=PLAYER;
  if(MODE==='hard'){setMap(HARD_STAGES[0])}
  else{let m='seoul';try{m=localStorage.getItem('drift-map')||'seoul'}catch(e){}setMap(MAPLABEL[m]?m:'seoul')}
  $('name').value=PLAYER;loadBoard();
}
MC.forEach(b=>b.onclick=()=>{
  const m=b.dataset.mode;
  if(m==='duel'){toast('1대1 대결은 곧 열려요. 방을 만들고 비밀번호로 친구와 달리는 모드예요.');b.classList.remove('shake');void b.offsetWidth;b.classList.add('shake');return}
  MODE=m;
  $('mnMode').textContent=MODENAME[m];$('mnMode').classList.toggle('hard',m==='hard');
  $('mnHint').textContent=m==='hard'?'스테이지를 클리어한 기록이 이 이름으로 하드 순위표에 올라가요.':'이 이름으로 기록이 맵별 순위표에 올라가요.';
  $('mnHint').classList.remove('err');
  $('mnName').value=PLAYER;$('mStep1').hidden=true;$('mStep2').hidden=false;
  setTimeout(()=>$('mnName').focus(),30);
});
$('mnBack').onclick=()=>{$('mStep1').hidden=false;$('mStep2').hidden=true};
$('mStep2').onsubmit=e=>{
  e.preventDefault();
  const n=$('mnName').value.trim().slice(0,20);
  if(!n){$('mnHint').textContent='이름을 입력해 주세요.';$('mnHint').classList.add('err');$('mnName').focus();return}
  PLAYER=n;try{localStorage.setItem('drift-name',n)}catch(e){}
  applyMode();
  $('modes').classList.remove('on');$('start').style.display='grid';
};
$('mbChange').onclick=showModes;
/* 하드 스테이지 목록 (홈) */
(function(){
  const row=$('stList');
  HARD_STAGES.forEach((id,i)=>{const d=document.createElement('div');d.innerHTML='<span></span><b></b>';d.children[0].textContent='STAGE '+(i+1);d.children[1].textContent=MAPLABEL[id];row.append(d)});
  const n=document.createElement('div');n.className='next';n.innerHTML='<span>NEXT</span><b>준비 중</b>';row.append(n);
})();

/* ---------- 홈 리더보드 버튼 ---------- */
function openLeaderboard(){const p=$('lbp');p.classList.add('top');p.classList.toggle('on');loadBoard()}
$('lbBtn').onclick=openLeaderboard;
addEventListener('keydown',e=>{if(e.key==='Escape'&&$('lbp').classList.contains('top'))$('lbp').classList.remove('on')});
document.querySelectorAll('.maps button').forEach(b=>b.onclick=()=>{if(b.dataset.map!==MAPID){setMap(b.dataset.map);loadBoard()}});

/* ---------- 플레이 시작 ---------- */
$('go').onclick=()=>{
  $('lbp').classList.remove('on','top');
  if(MODE==='hard')hardBegin();
  $('start').style.display='none';started=true;reset();
  stopAudio();initAudio();
};

/* ---------- 하드모드 ---------- */
const hardTotal=()=>stageTimes.reduce((a,b)=>a+b,0);
function updateHH(){
  $('hhStage').textContent='STAGE '+(hardIdx+1)+' / '+HARD_STAGES.length+' · '+MAPLABEL[HARD_STAGES[hardIdx]];
  const p=$('hhPips');while(p.children.length<HARD_HITS)p.append(document.createElement('i'));
  [...p.children].forEach((el,i)=>el.classList.toggle('x',i<hits));
  $('hhLeft').textContent='벽 충돌 '+hits+' / '+HARD_HITS;
}
function hardBegin(){
  hardIdx=0;hits=0;stageTimes=[];DEAD=false;HOLD=false;clearTimeout(failT);
  ['boom','fail','stg','hit'].forEach(i=>$(i).classList.remove('on','win','water'));
  if(MAPID!==HARD_STAGES[0])setMap(HARD_STAGES[0]);
  updateHH();$('hh').classList.add('on');
}
function wallHit(){
  if(DEAD||HOLD)return;
  const t=performance.now();if(t-lastHit<900)return;lastHit=t;
  hits++;updateHH();
  const h=$('hit');h.classList.remove('on');void h.offsetWidth;h.classList.add('on');
  if(hits>=HARD_HITS)explode();
}
function explodeSound(){
  if(!AC)return;try{AC.resume()}catch(e){}
  const t=AC.currentTime,sr=AC.sampleRate;
  const comp=AC.createDynamicsCompressor();comp.connect(AC.destination);
  const out=AC.createGain();out.gain.value=1;out.connect(comp);
  /* 1) 충격파: 낮게 내려앉는 사인 */
  const o=AC.createOscillator();o.type='sine';o.frequency.setValueAtTime(150,t);o.frequency.exponentialRampToValueAtTime(26,t+1.5);
  const og=AC.createGain();og.gain.setValueAtTime(.0001,t);og.gain.exponentialRampToValueAtTime(1.2,t+.015);og.gain.exponentialRampToValueAtTime(.001,t+1.7);
  o.connect(og);og.connect(out);o.start(t);o.stop(t+1.8);
  /* 2) 폭발 본체: 노이즈 + 닫혀가는 로우패스 */
  const nb=AC.createBuffer(1,Math.floor(sr*2.8),sr),nd=nb.getChannelData(0);
  for(let i=0;i<nd.length;i++)nd[i]=Math.random()*2-1;
  const ns=AC.createBufferSource();ns.buffer=nb;
  const lp=AC.createBiquadFilter();lp.type='lowpass';lp.frequency.setValueAtTime(7000,t);lp.frequency.exponentialRampToValueAtTime(140,t+1.9);
  const ng=AC.createGain();ng.gain.setValueAtTime(.0001,t);ng.gain.exponentialRampToValueAtTime(1.3,t+.01);ng.gain.exponentialRampToValueAtTime(.35,t+.35);ng.gain.exponentialRampToValueAtTime(.001,t+2.3);
  ns.connect(lp);lp.connect(ng);ng.connect(out);ns.start(t);ns.stop(t+2.6);
  /* 3) 금속 파편 튀는 소리 */
  for(let k=0;k<9;k++){
    const st=t+.08+Math.random()*1.3,s=AC.createBufferSource();s.buffer=nb;
    const bp=AC.createBiquadFilter();bp.type='bandpass';bp.frequency.value=700+Math.random()*3200;bp.Q.value=4+Math.random()*6;
    const g=AC.createGain();g.gain.setValueAtTime(.0001,st);g.gain.exponentialRampToValueAtTime(.35+Math.random()*.3,st+.004);g.gain.exponentialRampToValueAtTime(.001,st+.09+Math.random()*.1);
    s.connect(bp);bp.connect(g);g.connect(out);s.start(st,Math.random()*1.5);s.stop(st+.25);
  }
  /* 4) 불타는 지글거림 */
  const hp=AC.createBiquadFilter();hp.type='highpass';hp.frequency.value=2500;
  const fg=AC.createGain();fg.gain.setValueAtTime(.0001,t+.3);fg.gain.exponentialRampToValueAtTime(.16,t+.7);fg.gain.exponentialRampToValueAtTime(.001,t+2.8);
  const fs=AC.createBufferSource();fs.buffer=nb;fs.loop=true;fs.connect(hp);hp.connect(fg);fg.connect(out);fs.start(t+.3);fs.stop(t+2.9);
}
function explode(){
  DEAD=true;for(const k in keys)keys[k]=0;c.vx=c.vz=0;
  if(eg)eg.gain.value=0;if(sg)sg.gain.value=0;
  explodeSound();
  const b=$('boom');b.classList.remove('on','water');void b.offsetWidth;b.classList.add('on');
  let n=0;const sh=setInterval(()=>{hitK=1;if(++n>22)clearInterval(sh)},50);
  failT=setTimeout(()=>showFail(false),1900);
}
async function showFail(win,why){
  const cleared=stageTimes.length;
  $('fail').classList.toggle('win',win);
  $('failT').textContent=win?'ALL CLEAR':why==='water'?'추락':'실패';
  $('failSub').textContent=win?'모든 스테이지를 클리어했어요!':why==='water'?'바다에 빠졌어요. 점프할 때 속도가 모자랐거나 방향이 틀어졌어요.':'차량이 폭발했어요. 벽에 '+HARD_HITS+'번 부딪혔어요.';
  $('fStage').textContent=win?HARD_STAGES.length+' / '+HARD_STAGES.length:(hardIdx+1)+' / '+HARD_STAGES.length+' · '+MAPLABEL[HARD_STAGES[hardIdx]];
  $('fClear').textContent=cleared+'개';
  $('fTime').textContent=cleared?fmt(hardTotal()):'-';
  $('fHits').textContent=hits+'회';
  const net=$('failNet');
  $('fail').classList.add('on');$('hh').classList.remove('on');
  if(!cleared){net.textContent='스테이지를 1개 이상 클리어하면 순위표에 올라가요.';return}
  if(!PLAYER){net.textContent='';return}
  net.textContent='순위표에 올리는 중...';
  try{
    const res=await sendScore({name:PLAYER,lap_ms:hardTotal(),map:'hard',mode:'hard',stage:cleared});
    net.textContent=res==='ok'?'순위표에 기록했어요. (스테이지 '+cleared+' · '+fmt(hardTotal())+')':'하드 순위표는 아직 준비 중이에요.';
    if(res==='ok')loadBoard();
  }catch(e){net.textContent='기록을 올리지 못했어요.'}
}
function hardLapDone(t){
  if(DEAD||HOLD)return;
  stageTimes.push(t);
  for(const k in keys)keys[k]=0;c.vx=c.vz=0;
  if(hardIdx>=HARD_STAGES.length-1){DEAD=true;showFail(true);return}
  HOLD=true;
  $('stgT').textContent='STAGE '+(hardIdx+1)+' CLEAR';
  $('stgS').textContent=fmt(t)+' · 다음 '+MAPLABEL[HARD_STAGES[hardIdx+1]];
  $('stg').classList.add('on');
  setTimeout(()=>{
    hardIdx++;if(HARD_RESET_PER_STAGE)hits=0;
    setMap(HARD_STAGES[hardIdx]);updateHH();
    $('stg').classList.remove('on');HOLD=false;
  },2300);
}
/* 바다에 빠짐 (화물선 맵 점프 실패) */
function waterSound(){
  if(!AC)return;try{AC.resume()}catch(e){}
  const t=AC.currentTime,sr=AC.sampleRate,out=AC.createGain();out.gain.value=1;out.connect(AC.destination);
  const nb=AC.createBuffer(1,Math.floor(sr*2.6),sr),nd=nb.getChannelData(0);for(let i=0;i<nd.length;i++)nd[i]=Math.random()*2-1;
  const s=AC.createBufferSource();s.buffer=nb;const bp=AC.createBiquadFilter();bp.type='lowpass';bp.frequency.setValueAtTime(5000,t);bp.frequency.exponentialRampToValueAtTime(300,t+1.4);
  const g=AC.createGain();g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(1.1,t+.02);g.gain.exponentialRampToValueAtTime(.001,t+1.8);
  s.connect(bp);bp.connect(g);g.connect(out);s.start(t);s.stop(t+2);
  const o=AC.createOscillator();o.type='sine';o.frequency.setValueAtTime(90,t);o.frequency.exponentialRampToValueAtTime(35,t+.6);
  const og=AC.createGain();og.gain.setValueAtTime(.0001,t);og.gain.exponentialRampToValueAtTime(.9,t+.01);og.gain.exponentialRampToValueAtTime(.001,t+.8);o.connect(og);og.connect(out);o.start(t);o.stop(t+.9);
  for(let k=0;k<14;k++){const st=t+.5+Math.random()*1.6,b=AC.createBufferSource();b.buffer=nb;const f=AC.createBiquadFilter();f.type='bandpass';f.frequency.value=300+Math.random()*900;f.Q.value=12;
    const gg=AC.createGain();gg.gain.setValueAtTime(.0001,st);gg.gain.exponentialRampToValueAtTime(.5,st+.01);gg.gain.exponentialRampToValueAtTime(.001,st+.12);b.connect(f);f.connect(gg);gg.connect(out);b.start(st,Math.random());b.stop(st+.2)}
}
function hardWater(){
  if(DEAD)return;
  DEAD=true;for(const k in keys)keys[k]=0;c.vx=c.vz=0;
  if(eg)eg.gain.value=0;if(sg)sg.gain.value=0;
  waterSound();
  const b=$('boom');b.classList.remove('on');void b.offsetWidth;b.classList.add('on','water');
  failT=setTimeout(()=>showFail(false,'water'),1600);
}
/* 점프 안내 (화물선 맵) */
setInterval(()=>{
  const el=$('jh');
  if(!started||DEAD||HOLD||!JMP||AIR){el.classList.remove('on');return}
  const d=(JMP.iLip-ci)*SP;
  if(d<=0||d>160){el.classList.remove('on');return}
  const kmh=Math.hypot(c.vx,c.vz)*3.6,ok=kmh>=JMP.needKmh;
  $('jhD').textContent=Math.round(d)+'m';$('jhV').textContent=JMP.needKmh+' km/h 이상';
  el.classList.toggle('ok',ok);el.classList.add('on');
},100);
$('failRetry').onclick=()=>{hardBegin();reset();if(!AC)initAudio()};
$('failMenu').onclick=showModes;

/* ---------- 시작: 모드 선택 화면부터 ---------- */
$('start').style.display='none';
loadBoard();
