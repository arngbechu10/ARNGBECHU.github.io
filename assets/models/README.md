# 1대1 상대 차 3D 모델

사용자가 Sketchfab에서 받은 모델을 게임용으로 줄인 파일이에요.
Blender로 엔진 같은 안 보이는 부품을 빼고, 바퀴 4개(`WHEEL_FL/FR/RL/RR`)를 따로 떼었어요.
그다음 폴리곤을 줄이고, Draco 압축과 WebP 텍스처로 한 대 약 0.5MB가 됐어요.

| 파일 | 차 | 차체 색 (게임에서 바꿈) |
|---|---|---|
| gtr.glb | Nissan Skyline GT-R R34 | 베이사이드 블루 |
| gt3.glb | Porsche 911 GT3 RS (991.2) | 실버 |
| chal.glb | Dodge Challenger SRT | 실버 그레이 |
| f40.glb | Ferrari F40 | 로쏘 코르사 빨강 |
| mcl.glb | McLaren 720S | 원래 색(검정) |
| supra.glb | Toyota Supra MK4 | 슈퍼 화이트 (유리는 어둡게) |

원본 출처·라이선스(Sketchfab 페이지 주소, 만든 사람)는 아직 적지 못했어요. 받으면 여기에 적어 주세요.

## h2r.glb (Kawasaki Ninja H2R, 오토바이)
- 사용자가 보낸 Sketchfab glb(22만 면, 텍스처 없음) → Blender 4.0 decimate(큰 부품만) → gltf-transform weld/simplify(0.45)/dedup/prune/draco → 437KB.
- 크기: 길이 x축 약 2.57m(앞 = -x 쪽에 헤드라이트), 높이 y 1.32m. 차체 검정 + 초록 프레임.
- **아직 게임에서 안 씀.** 나중에 오토바이 1대1에서 상대 오토바이로 쓸 예정 (m3dLoad처럼 불러오기).

## cbr.glb (Honda CBR600RR, 오토바이, 2026-11-18)
- 사용자가 보낸 2021 CBR600RR glb(23만 면, 텍스처 49장) → 받침대 삭제, 차체 무늬를 사용자 바이크(무비스타 레이싱 컬러: 파랑·형광 연두·초록 아랫배)로 다시 칠함, 보조 텍스처(노멀 등) 빼고 재질값 직접, simplify·768px webp·draco → 634KB, 5.3만 면.
- 크기: 길이 x축 약 2.07m(앞 = +x), 높이 1.23m. 게임 설정 `M3D.cbr={bike:true,rotY:0}`.
- h2r.glb는 재질이 어두운 거울 금속이라 게임(`M3D.h2r.fix`)에서 검정 광택 페인트로 바꿔 보여 줘요.
