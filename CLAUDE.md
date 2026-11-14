# Arngbechu Racing (예전 이름: R34 드리프트 랩타임) — 프로젝트 요약 (claude.ai 채팅에서 옮겨옴)

고등학생(자동차공학과 희망)이 재미로 만드는 **브라우저 1인칭 운전 게임**이에요. 친구들과 랩타임 순위를 겨루는 게 목적이고, GitHub Pages로 배포하고 Supabase로 순위표를 저장합니다.
사용자와는 **한국어**로, 쉽고 짧게 이야기해 주세요. 사용자는 PC와 삼성 태블릿·폰(가로 화면)에서 테스트해요.

## 파일 구성

| 경로 | 설명 |
|---|---|
| `index.html` | **실제 게임 전체 (약 6MB, 파일 하나)**. 이미지·소리가 전부 base64로 들어 있어요. 배포는 이 파일 하나면 됩니다. |
| `index.readable.html` | base64를 `DATAURI`로 바꾼 읽기 전용 사본 (줄 번호 원본과 같음). `python3 tools/strip_data_uris.py`로 다시 만들 수 있어요. |
| `supabase_setup.sql` | 순위표를 맵·모드별로 나누는 SQL. **2026-11-14 사용자가 실행 완료**(Success). |
| `assets/` | 게임에 들어간 원본 에셋: 차량 이미지(앞모습·콕핏·핸들, 720S 뒷모습), 엔진·시동 소리(wav), 사용자가 보낸 원본 엔진 녹음(mp3), 맵 하늘·바다 이미지 |
| `build/` | 채팅에서 쓰던 **빌드 기록 (참고용)**. 중간 파일(t_nitro.html 등)이 없어서 그대로 다시 돌리진 못해요. 앞으로는 `index.html`을 직접 고치면 됩니다. |
| `tests/` | Playwright 테스트 스크립트 (참고용, 경로는 채팅 환경 기준이라 수정 필요) |

**편집 팁:** `index.html`의 base64 줄은 매우 길어요. 파일 전체를 읽지 말고 `index.readable.html`에서 위치를 찾은 뒤, 원본에서 짧은 고유 문자열로 찾아 바꾸세요. 새 이미지/소리를 넣을 때도 base64 data URI로 넣는 방식을 유지합니다(소리는 `b64buf()`가 data URI를 직접 디코드함).

## 기술 구성
- Three.js **r128** (`https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`), 조명 없는 `MeshBasicMaterial` 위주. WebGL 장면 위에 CSS로 콕핏 이미지(.cab 3:1 비율, `#cabin`, `#wheel`, 속도계 `#gg`)를 겹쳐요.
- 소리: Web Audio. 엔진 루프를 `playbackRate`로 회전수에 맞춰 바꾸고, 미끄럼·니트로·충돌·폭발·물 소리는 코드로 합성.
- 저장: `localStorage` 키 `drift-ctl2`(조작 버튼 배치), `drift-map`, `drift-car`, `drift-name`.

## 코드 지도 (`index.readable.html` 줄 번호 기준, 대략)
| 줄 | 내용 |
|---|---|
| 7–272 | CSS (164~ 모드 선택·이름 입력, 220~ 하드모드 HUD/폭발/실패/점프 안내) |
| 274–406 | HTML: 게임 HUD, 리더보드 패널 `#lbp`, 홈 `#start`, 모드 선택 `#modes`, 하드 HUD `#hh`, 점프 안내 `#jh`, 폭발 `#boom`, 스테이지 배너 `#stg`, 실패 창 `#fail`, 조작 편집기 `#ced` |
| 423–683 | **맵 시스템**: `SKIES`, `MAPS` 설정, 도로 띠 `strip()`, 바리케이드 `wallStrip()`, 나무, 산 지형 `buildTerrain()`, 서울 다리 `planBridge()/buildBridge()` |
| 684–837 | **화물선 맵**: `SH` 치수, `shipPlan()`(점프 위치·장애물 `OBS`), `buildShip()`, `obsCollide()`, `launch()`, `airStep()`(공중 물리), `onWater()` |
| 838–905 | `setMap(id)`: 코스 점 N=1400개, 높이 `TY`, 경사 `TSL`, 법선 `TN`, 방향 `TH` 계산 후 맵 생성 |
| 923–999 | **차량 물리** `step(dt)`: 가속·그립·드리프트, 벽 충돌(`WALL`), 경사, 한 바퀴 판정(`prog>=LAPEND`) |
| 1000–1052 | 엔진 소리 `initAudio()`, `drive()`(회전수·기어·속도계·소리 크기) |
| 1053–1123 | 미니맵, 니트로(한 바퀴에 한 번, 4초) |
| 1124–1146 | 메인 루프 `loop()` (카메라 높이는 지면 `TY` 또는 공중일 때 `cy`) |
| 1147–1292 | 홈: 방향키 모양 선택, 조작법 탭, 터치 버튼 편집기 |
| 1293–1324 | **차량 선택** `CARS` (gtr, gt3, chal, f40, mcl + 잠긴 Tesla) |
| 1325–1389 | **리더보드** Supabase (`loadBoard`, `sendScore`, `doSend`) |
| 1390–1450 | 모드 선택 → 이름 입력 → 홈, 플레이 시작 버튼 |
| 1451–1580 | **하드모드** (`HARD_STAGES`, 충돌 카운트, 폭발, 추락, 스테이지 클리어, 실패 창, 점프 안내) |

## 지금까지 만든 기능
- **모드 선택 화면**(시작하자마자, 카드 큰 글씨: 1 : 1 / LAP / PRACTICE ZONE(두 줄, `.mc i.two`) / HARD): 1대1 대결, 개인 랩타임, **연습장**, 하드 랩타임 → 이름 입력(연습장은 건너뜀) → 홈. 홈 왼쪽 위에 모드·이름·"모드 변경". 운전 중 오른쪽 위 **"← 나가기"** 버튼(`#back`, Esc 키도) → 홈(차 선택)으로(`goBack()`): 하드는 확인 후 1스테이지로 초기화, 1대1은 확인 후 방 나가기(모드 선택). 1대1 카드의 NEW 표시는 지움.
- **차량 5대**: Nissan Skyline GT-R R34(기본, 오른쪽 핸들), Porsche 911 GT3 RS, Dodge Challenger SRT, Ferrari F40, McLaren 720S. 차마다 콕핏 이미지·핸들 위치·엔진 소리 다름(물리는 모두 같음). 왼쪽 핸들 차는 속도계가 오른쪽(gx 71).
  - 차량 선택창 차 이름 아래에 **실제 차 정보**(마력·무게·0→100·최고 속도·구동 방식 + 한 줄 특징, `CSPEC`/`showSpec()`)와 "실제 차 정보예요. 게임 속 성능은 모두 같아요" 안내.
  - Tesla Roadster 타일은 눌러도 선택 안 되고 "이딴건 차가 아닙니다 사용하실 수 없습니다" 토스트(사용자 요청 문구 그대로 유지).
  - 엔진음: 사용자가 보낸 녹음에서 안정 구간을 잘라 루프로 만듦. 시동음은 실제 녹음이 없어 **합성**(스타터→점화→아이들).
- **맵** (개인 랩타임·1대1에서 선택): Seoul(야경, 바리케이드, 한강다리 같은 다리), Mountain Pass(내리막 산길, 가드레일, 지형·나무), Christmas(눈, 조명 울타리), **Tokyo Neon**(어려움), **New York**(어려움).
- **Tokyo Neon City** (맵 id `tokyo`, 코드는 `Tokyo Neon City 맵` 주석 블록 ~ `/* === Tokyo 끝 === */`, `MAPS` 바로 뒤에 있어야 함: 저장된 맵이 tokyo면 시작할 때 바로 만들어지므로): 비 오는 밤 시가지 1.28km(`TOKYO_CTRL`), 도로 반폭 7.5, 90도 코너·헤어핀·S자 시케인(반경 10~12m). 하늘은 사용자가 보낸 사진 3장을 이어 만든 파노라마(`assets/maps/sky_tokyo.webp`, 썸네일 `thumb_tokyo.webp`). 장애물 `TOKYO_OBS`(f=코스 비율, lat=+오른쪽): 工事中 공사 구간 2곳(바리케이드·깜빡이 경고등·인사하는 작업자 간판·화살표 판), 주차된 택시(비상등), 자판기 3대, 도리이 6개(`TORII_F`, 기둥 ±6.1m가 도로 안). 충돌은 회전된 상자 `tobsCollide()`(`TOBS`). 장식: 창문 건물(바깥쪽 높고 안쪽은 1~3층 가게), 네온 간판 아틀라스(`NEON`/`BOARDS`), 젖은 도로 네온 반사, 3D 도쿄 타워(코스 안쪽 70,130), 초록 고속도로 표지판(東京タワー·銀座·渋谷 등), 코너 쉐브론, 벚꽃, 빨간 초롱, 비(`tokyoFrame`). 같은 재질은 `tkAdd`/`tkFlush`로 합쳐서 물체 약 70개. 도로 폭은 나중 1대1을 위해 차 2대가 넉넉히 들어가게 넓혀 둠.
- **New York Downtown** (맵 id `ny`, 코드는 `New York Downtown 맵` 주석 블록 ~ `/* === New York 끝 === */`, Tokyo 블록 바로 뒤, Tokyo 도구 `tkAdd/tkFlush/tkAt/winTex/TOBS` 재사용): 밤 2.1km(`NY_CTRL`), 반폭 9. 타임스스퀘어 광고판 직선(`nyAtlas`) → 다운타운 코너 → **브루클린 다리**(z=130 직선, 높이 `NY_DECK`=9m, `MAPS.ny.tyFn=nyTY`로 경사로, 강 `NY_WATER` 위) 돌탑 2개(`NY_TOWERS`, 가운데 기둥이 장애물이라 왼쪽/오른쪽 아치로 통과), 케이블·전구 → 워싱턴 스퀘어 개선문(기둥은 도로 밖) → 북적이는 거리. 장애물 `NY_OBS`(at=[x,z] 근처 코스 점, lat=+오른쪽): 이중 주차 노란 택시 3대, 증기 굴뚝 2개(증기 `nyFrame`), ROAD WORK 공사 구간 1곳. 장식: 빌딩(물탱크·첨탑), 초록 고속도로 표지판(I-95 등), 가로등+NEW YORK 깃발, 가로수, 소화전, 보도 위 사람들, 쉐브론. 하늘은 사용자 사진 3장 파노라마 `assets/maps/sky_ny.webp`, 미니맵에 강(`mmNY`). `setMap`은 `D.tyFn`이 있으면 높이를 그걸로, 맵 바꿀 때 `TOBS=[]`, 충돌은 `TOBS.length`면 항상 검사.
- **하드 랩타임**: 스테이지마다 허용 충돌 횟수가 줄어듦(`hardLimit(i)=HARD_FIRST(10)-i`, 최소 `HARD_MIN`): 1스테이지 10번 → 9 → 8 → 7 (맵 6개면 10~5). 충돌 횟수는 스테이지마다 새로 셈, 실패 창의 "벽 충돌 (전체)"는 `hitsTotal`. 넘으면 폭발음+연출 후 "실패". 스테이지를 차례로 클리어: Christmas → Seoul → Mountain Pass → **Cargo Ship**. R(재시작) 키 막음. 새 스테이지는 `HARD_STAGES` 배열에 맵 id만 추가.
- **Cargo Ship(화물선 탈출)**: 편도 코스(`open:true`, 결승 `LAPEND`). 선미 출발 → 컨테이너 장애물 슬랄롬 → 뱃머리 점프대 → 바다 48m 점프 → 부두 착지 → 결승. 필요 속도 약 90km/h(`needSpeed()`로 계산, 화면 위 JUMP 안내). 못 넘으면 "추락" 실패. 이 맵은 하드모드 전용(홈 맵 목록에는 없음). 점프 물리는 이 맵에만 있음.
- **1대1 대결**: 모드 선택 → 이름 → 방 만들기(맵 고르기 → 4자리 방 비밀번호) / 방 참가(비밀번호 입력) → 둘 다 차고에서 차 고르고 "준비" → 나란히 서서 5,4,3,2,1 GO! → `DUEL_LAPS`(3)바퀴 먼저 완주하면 승리(기록 비교). 상대 차는 **실제 사진**(뒷모습 `assets/cars/rear_*.webp`, 앞모습은 홈 사진)을 범퍼 위치에 바닥에 붙여 세우고 카메라 쪽으로 돌림(`oppVisual`, 설정 `CARV`). 보는 쪽에 따라 좌우 반전, 바닥 그림자, 스프링·댐퍼 롤/피치(차체 위쪽만 기울임), 브레이크 등·니트로 불꽃·드리프트 연기(상대가 보내는 `f` 플래그). 차 5대 모두 뒷모습 사진 있음(사진이 없으면 상자 차 `BOXM`으로 대체). 새 사진은 rembg(isnet-general-use)로 배경 제거 → 640px webp → `REAR`/`CARV`에 추가. 머리 위 "OPPONENT" 이름표, 미니맵에 빨간 점. 차끼리 부딪히면 속도를 나누고 살짝 튕겨 나감(`duelCollide`). 상대가 나가면 알림.
  - **3D 모델**(`assets/models/<차>.glb`, 설명은 그 폴더 README): 상대 차가 정해지면 `m3dLoad()`로 그 차만 불러와 `opp3D()`로 표시(사진 방식은 못 불러올 때만). GLTFLoader/DRACOLoader는 jsDelivr three@0.128.0에서 필요할 때만. `M3D`: 차체 재질 이름 정규식 `paint`와 색 `col`(홈 사진과 비슷하게). 차체(`body`)만 롤·피치로 기울이고, 바퀴는 속도/반지름만큼 굴러가고 앞바퀴는 조향(`V.st`). 빛: 반구광+태양광(맵별 밝기 `M3L`), 반사는 하늘 사진(`m3dEnvFor`). 모델 앞=+z, `holder.rotation.y=π/2`로 게임 앞(+x)에 맞춤. 변환은 Blender 4.0(`apt install blender python3-numpy`) 스크립트로: 부모 풀기 → 메쉬 아닌 것·엔진 지우기 → 합치기 → 길이 맞추기 → 바퀴 재질 면을 위치로 4개 분리 → 용접·decimate(차체 4.5만, 바퀴 2.5천 삼각형) → glb, 그다음 `gltf-transform` dedup/prune/resize 512/webp/draco. F40은 obj 왕복(`viaobj`)과 부품별 미리 줄이기(`preDec`, tailgate 제외)가 필요했음.
  - **출발 부스터(런치 컨트롤)**, 1대1에만(`LC`, `lcTick`/`lcGo`, 화면 `#lc` 바·`#lcr` 결과 글씨): 카운트다운 중 가속을 누르면 바늘이 초당 0.62씩 오르고 떼면 0.85씩 내려감. GO 순간 0.665~0.735면 PERFECT(1.3초 추가 가속 7 + 니트로 화면 효과·소리), 0.6~0.8면 GOOD(0.8초 추가 가속 5), 0.88 이상이면 WHEELSPIN(1.1초 가속 12%, 타이어 소리·흔들림), 그 밖은 보통. 2초 뒤 속도: 보통 76, GOOD 86, PERFECT 97, 휠스핀 41 km/h. 부스트 중엔 상대에게 니트로 불꽃(`f` 8), 휠스핀은 연기(`f` 4). 테스트 주의: 두 페이지 중 뒤에 있는 탭은 requestAnimationFrame이 멈추므로 `bringToFront()` 하거나 `lcTick`/`step`을 직접 호출.
  - 상대 위치는 **스냅샷 보간**(`oppPos`가 보낸 시각 `t`와 함께 버퍼에 쌓고, `oppSample`이 0.12초(`OPP_DELAY`) 전 시점을 두 스냅샷 사이 Hermite 곡선으로 계산, 시계 차이는 천천히 맞춤). 사진·그림자 높이는 `groundAt()`으로 그 자리 도로 높이. 피치는 상대 브레이크/가속 입력으로만, 롤은 실제 코너링(횡가속 1.5m/s² 이상)에서만.
  - 통신: Supabase Realtime 채널 `drift-duel-<비밀번호>` (presence로 방 인원, broadcast `m` 이벤트로 `hi/room/car/go/p/fin/bye` 메시지). supabase-js 2.117.3을 jsDelivr에서 1대1을 열 때만 불러옴. DB 설정은 필요 없음.
  - 코드: `index.readable.html`에서 `1대1 대결` 주석 블록(파일 끝 근처). 로비 HTML은 `#mStep3`, 경주 HUD `#dh`, 카운트다운 `#cd`, 결과 `#dres`.
  - 테스트: Supabase 대신 BroadcastChannel로 흉내 내는 가짜 라이브러리를 Playwright에서 `**/supabase-js@*/**` 요청에 넣고, 한 브라우저 컨텍스트에 페이지 2개(가·나)를 열어 확인.
- **연습장** (`MODE='practice'`, 맵 id `practice`, 코드는 `연습장` 주석 블록): 520m×520m 평지(`PA=260`), 타이어 벽(`practiceBounds()`), 구역 `PZ`: 드리프트 원(콘 둘레), 8자 코스, 슬라럼(콘 16개), 430m 직선 가속(100m 표지판, BRAKE). 콘은 부딪히면 쓰러짐(`CONES`, R/처음 위치 버튼으로 원위치). HUD `#ph`: 드리프트 각도·시간·최고, 최고 속도. 랩·타이머·순위표 없음, 니트로는 끝나고 5초 뒤 다시 참. 코스 점 `TP`는 바깥 테두리 사각형(미니맵용), `half:600`이라 도로 밖 감속·밀어내기 없음. 바닥은 잘게 나눈 판 + 잔디는 2.5m 아래(깊이 겹침 방지), 바닥 표시는 polygonOffset.
- **리더보드**: 개인 랩타임은 새 최고 기록을 자동으로 올리고 맵별로 표시. 순위표 칸 위에 맵 탭(`LB_MAPS`: Seoul·Mountain·Christmas·Tokyo·New York, `loadBoard(m)`/`LBMAP`)으로 다른 맵 순위도 볼 수 있음(하드에선 탭 숨김). 하드는 클리어한 스테이지 수(많은 순) → 누적 시간(짧은 순). 홈의 "리더보드" 버튼으로도 열림.
- 기타: 니트로(한 바퀴 1번), 드리프트(핸드브레이크) 누를 때만 타이어 소리(`buildSkid`/`skidMix`: 사용자가 보낸 실제 드리프트 녹음 `assets/sounds/original/drifting_sound.mp3`의 1.0~5.35초 끽 소리를 4초 루프 `assets/sounds/skid_loop.wav`로 만들어 `SKIDSND`에 넣음. 미끄러짐에 따라 크기·재생 속도 조절), 핸드브레이크 중 회전량 ×1.7, 터치 버튼 모양/위치/크기/투명도 편집, 미니맵.

- **폰 가로 화면 전용 레이아웃**: CSS 끝의 `@media (orientation:landscape) and (max-height:500px)` 블록(PC·태블릿은 높이가 커서 영향 없음). 홈은 왼쪽(차·맵·플레이)/오른쪽(조작 설정) 두 칸이 각각 스크롤, 플레이 버튼은 아래에 고정. 운전 화면은 미니맵·HUD 축소, 콕핏 이미지를 135%로 키워(top:-14%, 사용자가 고른 B안: 핸들 위쪽 절반 보임) 천장선은 화면 맨 위·대시보드는 아래로 가서 도로가 넓게 보이고 속도계는 가운데 아래. 모드 선택 카드 3장 한 줄. 테스트는 Playwright `devices['iPhone 13 landscape']`(750×342), `Galaxy S9+ landscape`(658×320).

## Supabase
- URL `https://payqqpkkdpydypinyptz.supabase.co`, 표 `scores`(name, lap_ms + SQL 실행 후 map, mode, stage), publishable 키는 index.html 안에 있음(공개용 키, RLS로 select/insert만 허용).
- 코드는 열이 없으면(400 오류) 자동으로 예전 방식으로 돌아가요: 그때는 **Seoul 개인 기록만** 올라가고 나머지는 "순위표 준비 중".
- claude.ai 아티팩트에서는 외부 접속이 막혀 순위표가 안 됨 → 친구들과는 GitHub Pages 버전 사용.

## 앞으로 할 일 / 약속한 것
1. 하드모드 스테이지 맵 추가(사용자가 아이디어를 낼 예정). 화물선 맵의 장애물 간격·필요 속도·바다 폭은 `SH`/`shipPlan()` 숫자로 조절.
2. 사용자가 실제로 들어보고 엔진/시동/폭발 소리 피드백을 줄 수 있음(전부 확인 못 한 상태).

## 테스트 방법 (채팅에서 하던 방식)
- Playwright + Chromium(swiftshader)으로 열고, CDN 요청은 로컬 three.js 0.128.0으로 대체(`npm i three@0.128.0`), Supabase 요청은 가짜 응답으로 대체.
- 홈 진입: 모드 카드 클릭 → `#mnName` 입력 → Enter → `#go`. 잠긴 카드(aria-disabled)는 `force=True`로 클릭.
- 헤드리스에서는 프레임이 느려서 물리 시간이 실제보다 천천히 흐름 → 기다리는 시간을 넉넉히.
- 스크립트 문법 검사: `<script>` 내용을 뽑아 `node --check`.
