# R34 드리프트 랩타임 — 프로젝트 요약 (claude.ai 채팅에서 옮겨옴)

고등학생(자동차공학과 희망)이 재미로 만드는 **브라우저 1인칭 운전 게임**이에요. 친구들과 랩타임 순위를 겨루는 게 목적이고, GitHub Pages로 배포하고 Supabase로 순위표를 저장합니다.
사용자와는 **한국어**로, 쉽고 짧게 이야기해 주세요. 사용자는 PC와 삼성 태블릿·폰(가로 화면)에서 테스트해요.

## 파일 구성

| 경로 | 설명 |
|---|---|
| `index.html` | **실제 게임 전체 (약 6MB, 파일 하나)**. 이미지·소리가 전부 base64로 들어 있어요. 배포는 이 파일 하나면 됩니다. |
| `index.readable.html` | base64를 `DATAURI`로 바꾼 읽기 전용 사본 (줄 번호 원본과 같음). `python3 tools/strip_data_uris.py`로 다시 만들 수 있어요. |
| `supabase_setup.sql` | 순위표를 맵·모드별로 나누려면 Supabase SQL Editor에서 **한 번 실행해야 하는 SQL** (아직 사용자가 실행 안 했을 수 있음). |
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
- **모드 선택 화면**(시작하자마자): 1대1 대결(잠김, "준비 중"), 개인 랩타임, 하드 랩타임 → 이름 입력 → 홈. 홈 왼쪽 위에 모드·이름·"모드 변경".
- **차량 5대**: Nissan Skyline GT-R R34(기본, 오른쪽 핸들), Porsche 911 GT3 RS, Dodge Challenger SRT, Ferrari F40, McLaren 720S. 차마다 콕핏 이미지·핸들 위치·엔진 소리 다름(물리는 모두 같음). 왼쪽 핸들 차는 속도계가 오른쪽(gx 71).
  - Tesla Roadster 타일은 눌러도 선택 안 되고 "이딴건 차가 아닙니다 사용하실 수 없습니다" 토스트(사용자 요청 문구 그대로 유지).
  - 엔진음: 사용자가 보낸 녹음에서 안정 구간을 잘라 루프로 만듦. 시동음은 실제 녹음이 없어 **합성**(스타터→점화→아이들).
- **맵** (개인 랩타임에서 선택): Seoul(야경, 바리케이드, 한강다리 같은 다리), Mountain Pass(내리막 산길, 가드레일, 지형·나무), Christmas(눈, 조명 울타리). 도로 폭은 나중 1대1을 위해 차 2대가 넉넉히 들어가게 넓혀 둠.
- **하드 랩타임**: 벽/장애물에 5번 부딪히면 폭발음+연출 후 "실패". 스테이지를 차례로 클리어: Christmas → Seoul → Mountain Pass → **Cargo Ship**. 충돌 횟수는 도전 전체 합산(`HARD_RESET_PER_STAGE=false`로 바꿀 수 있음). R(재시작) 키 막음. 새 스테이지는 `HARD_STAGES` 배열에 맵 id만 추가.
- **Cargo Ship(화물선 탈출)**: 편도 코스(`open:true`, 결승 `LAPEND`). 선미 출발 → 컨테이너 장애물 슬랄롬 → 뱃머리 점프대 → 바다 48m 점프 → 부두 착지 → 결승. 필요 속도 약 90km/h(`needSpeed()`로 계산, 화면 위 JUMP 안내). 못 넘으면 "추락" 실패. 이 맵은 하드모드 전용(홈 맵 목록에는 없음). 점프 물리는 이 맵에만 있음.
- **리더보드**: 개인 랩타임은 새 최고 기록을 자동으로 올리고 맵별로 표시. 하드는 클리어한 스테이지 수(많은 순) → 누적 시간(짧은 순). 홈의 "리더보드" 버튼으로도 열림.
- 기타: 니트로(한 바퀴 1번), 드리프트(핸드브레이크) 누를 때만 타이어 소리, 터치 버튼 모양/위치/크기/투명도 편집, 미니맵.

## Supabase
- URL `https://payqqpkkdpydypinyptz.supabase.co`, 표 `scores`(name, lap_ms + SQL 실행 후 map, mode, stage), publishable 키는 index.html 안에 있음(공개용 키, RLS로 select/insert만 허용).
- 코드는 열이 없으면(400 오류) 자동으로 예전 방식으로 돌아가요: 그때는 **Seoul 개인 기록만** 올라가고 나머지는 "순위표 준비 중".
- claude.ai 아티팩트에서는 외부 접속이 막혀 순위표가 안 됨 → 친구들과는 GitHub Pages 버전 사용.

## 앞으로 할 일 / 약속한 것
1. **1대1 모드** (사용자가 "게임 구상 다 하고 깃허브 하면서" 다시 요청할 예정): 방 만들기 + 방 비밀번호를 친구와 공유해 같은 코스에서 경주. Supabase Realtime(broadcast/presence)로 위치 동기화 예정.
   - 요청받으면 **먼저 필요한 정보를 정리해서 알려주기로 약속함**: 상대 차를 앞에서 보이게 하려면 **각 차의 뒷모습 이미지**가 필요(720S 뒷모습은 `assets/cars/rear_mcl.webp`에 이미 있음, GT-R·GT3 RS·Challenger·F40은 없음).
   - 그때 **차끼리 부딪히면 옆으로 살짝 튕기는 충돌**도 같이 구현하기로 함.
2. 사용자가 `supabase_setup.sql`을 실행했는지 확인.
3. 하드모드 스테이지 맵 추가(사용자가 아이디어를 낼 예정). 화물선 맵의 장애물 간격·필요 속도·바다 폭은 `SH`/`shipPlan()` 숫자로 조절.
4. 사용자가 실제로 들어보고 엔진/시동/폭발 소리 피드백을 줄 수 있음(전부 확인 못 한 상태).

## 테스트 방법 (채팅에서 하던 방식)
- Playwright + Chromium(swiftshader)으로 열고, CDN 요청은 로컬 three.js 0.128.0으로 대체(`npm i three@0.128.0`), Supabase 요청은 가짜 응답으로 대체.
- 홈 진입: 모드 카드 클릭 → `#mnName` 입력 → Enter → `#go`. 잠긴 카드(aria-disabled)는 `force=True`로 클릭.
- 헤드리스에서는 프레임이 느려서 물리 시간이 실제보다 천천히 흐름 → 기다리는 시간을 넉넉히.
- 스크립트 문법 검사: `<script>` 내용을 뽑아 `node --check`.
