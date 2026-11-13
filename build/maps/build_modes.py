import re
W='/tmp/claude-0/-home-claude/f9ae0b19-9e15-514d-b64c-42a1ff34b6c5/scratchpad/'
h=open(W+'w/t_ship.html',encoding='utf-8').read()
css=open(W+'w/maps/modes.css',encoding='utf-8').read()
js=open(W+'w/maps/modes.js',encoding='utf-8').read()

def rep1(old,new):
    global h
    assert h.count(old)==1,(old[:90],h.count(old))
    h=h.replace(old,new)

# ---------- CSS ----------
rep1("</style>\n</head>",css+"</style>\n</head>")

# ---------- HTML ----------
rep1('<div id="toast" role="alert" aria-live="assertive"></div>','''<div id="modes" class="on" role="dialog" aria-label="모드 선택">
  <div class="bg"></div>
  <h1><small>R34 DRIFT LAP TIME</small>모드 선택</h1>
  <div class="mcards" id="mStep1">
    <button class="mc locked" data-mode="duel" aria-disabled="true"><span class="tag">준비 중</span><i>1 : 1</i><b>1대1 대결</b><p>방을 만들고 비밀번호를 정해서 친구와 같은 코스를 달려요.</p><ul><li>방 + 비밀번호</li><li>친구와 함께</li></ul></button>
    <button class="mc" data-mode="lap"><i>LAP</i><b>개인 랩타임</b><p>혼자 한 바퀴 기록에 도전해요. 맵마다 순위표가 따로 있어요.</p><ul><li>맵 3개</li><li>맵별 순위표</li></ul></button>
    <button class="mc hard" data-mode="hard"><i>×5</i><b>하드 랩타임</b><p>벽에 5번 부딪히면 차가 폭발해요. 스테이지를 하나씩 올라가요.</p><ul><li>충돌 5회 실패</li><li>스테이지 진행</li><li>순위표</li></ul></button>
  </div>
  <form class="mname" id="mStep2" hidden autocomplete="off">
    <span class="mchip" id="mnMode"></span>
    <label for="mnName">이름</label>
    <input id="mnName" maxlength="20" placeholder="순위표에 올라갈 이름 (20자 이내)" autocomplete="off">
    <p class="hint" id="mnHint"></p>
    <div class="mrow"><button type="button" class="mbtn ghost" id="mnBack">뒤로</button><button type="submit" class="mbtn play">시작하기</button></div>
  </form>
</div>
<div id="hh"><b id="hhStage"></b><div id="hhPips"></div><small id="hhLeft"></small></div>
<div id="hit"></div>
<div id="jh" role="status"><b>JUMP</b><span id="jhD"></span><em id="jhV"></em></div>
<div id="boom"><i class="f1"></i><i class="f2"></i><i class="sm"></i></div>
<div id="stg" role="status"><b id="stgT"></b><span id="stgS"></span></div>
<div id="fail" role="alertdialog" aria-labelledby="failT"><div class="fcard">
  <h2 id="failT"></h2><p id="failSub"></p>
  <dl><dt>도달 스테이지</dt><dd id="fStage"></dd><dt>클리어</dt><dd id="fClear"></dd><dt>누적 시간</dt><dd id="fTime"></dd><dt>벽 충돌</dt><dd id="fHits"></dd></dl>
  <p class="net" id="failNet"></p>
  <div class="mrow"><button class="mbtn play" id="failRetry">다시 도전</button><button class="mbtn ghost" id="failMenu">모드 선택</button></div>
</div></div>
<div id="toast" role="alert" aria-live="assertive"></div>''')
rep1('<div id="start">\n  <div class="bg"></div>','<div id="start" style="display:none">\n  <div class="bg"></div>\n  <div class="modebar"><span class="mchip" id="mbMode"></span><span>이름 <b id="mbName"></b></span><button id="mbChange" type="button">모드 변경</button></div>')
rep1('    <div class="cta">\n      <button class="btn play" id="go">','    <div class="stages"><div class="stl" id="stList"></div><p>스테이지를 하나씩 클리어해요. 벽이나 장애물에 5번 부딪히면 폭발!</p></div>\n    <div class="cta">\n      <button class="btn play" id="go">')
rep1('<h2>리더보드</h2>','<h2 id="lbTitle">리더보드</h2>')

# ---------- JS 패치 ----------
rep1("if(started)step(dt);","if(started&&!HOLD&&!DEAD)step(dt);")
rep1("if(l==='r')reset();","if(l==='r'&&MODE!=='hard')reset();")
rep1("if(vn>2.5)thump(Math.min(1,vn/14));","if(vn>2.5)thump(Math.min(1,vn/14));if(MODE==='hard'&&vn>3.5)wallHit();")
old="if(bestLap===null||t<bestLap){bestLap=t;$('best').textContent=fmt(t);$('send').disabled=MAPID!=='seoul';\n        $('msg').textContent=MAPID==='seoul'?'새 기록이에요! 이름을 적고 올려보세요.':'새 기록이에요! (이 맵 순위표는 아직 준비 중이에요)';$('lbp').classList.add('on')}"
rep1(old,"if(MODE==='hard'){hardLapDone(t)}else if(bestLap===null||t<bestLap){bestLap=t;$('best').textContent=fmt(t);$('send').disabled=false;\n        $('msg').textContent='새 기록이에요!';$('lbp').classList.add('on');autoSend()}")
rep1("try{localStorage.setItem('drift-map',id)}catch(e){}\n}","if(MODE!=='hard'){try{localStorage.setItem('drift-map',id)}catch(e){}}\n}")
rep1("eg.gain.value=(.25+.45*rpm*(keys.gas?1:.55))","eg.gain.value=(DEAD?0:1)*(.25+.45*rpm*(keys.gas?1:.55))")
# 리더보드/시작 버튼 구형 블록 교체
i=h.index("$('go').onclick=()=>{$('start').style.display='none';started=true;reset();initAudio()};")
j=h.index("/* ---------- 리더보드 (Supabase) ---------- */")
k=h.index("loadBoard();\n</script>")
h=h[:i]+js+h[k+len("loadBoard();\n"):]
rep1("function openLeaderboard(){}\n$('lbBtn').onclick=()=>openLeaderboard();\n","")
open(W+'w/t_modes.html','w',encoding='utf-8').write(h)
print('built',len(h))
