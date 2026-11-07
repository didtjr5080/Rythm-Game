# Codex 작업 지시서: EMG Motion Rhythm 'Glassmorphism Sonic Lab' 전면 UI/UX 개편 명세서

## 1. 작업 목적 및 컨텍스트 요약 (Objective & Context)

본 작업 지시서는 [EMG Motion Rhythm 리포지토리](https://github.com/didtjr5080/Rythm-Game)의 PyQt6 데스크톱 애플리케이션([app/ 디렉터리](https://github.com/didtjr5080/Rythm-Game/tree/main/app)) UI/UX를 첨부된 2장의 레퍼런스 시안(**Image 1: 인게임 플레이 및 실시간 웹캠 HUD 화면**, **Image 2: 선곡·캘리브레이션·재활 분석 3단 대시보드 화면**)과 동일한 **'Glassmorphism Sonic Lab'** 테마로 전면 리팩토링하기 위한 명세서입니다.

* **핵심 설계 목표**: 건양대학교 KY ANCHOR 사업단 캡스톤디자인 경진대회 본선 실시간 시연(5분 발표 + 3분 질의응답) 평가 기준(창의·융합성 30점, 교과목 연계성 25점, 기술성 및 완성도 25점, 기획성·전시효과 10점, 성실도·홍보효과 10점)에 맞춰, **화려한 3D 글래스모피즘 리듬게임의 시각적 전시효과**와 **실시간 생체신호(EMG) DSP·컴퓨터 비전(MediaPipe) 공학 텔레메트리 및 재활 수행도 지표**를 한 화면에 통합합니다.
* **불변 제약 사항 (Non-Breaking Constraints)**:
  * 기존 핵심 게임 루프 및 판정 엔진([app/game/rhythm_game_engine.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/game/rhythm_game_engine.py), [app/game/judge.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/game/judge.py), [app/game/note.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/game/note.py))의 판정 데이터 구조와 멀티모달 센서 결합([app/input/input_fusion.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/input/input_fusion.py))의 시그널/슬롯 인터페이스는 깨지지 않도록 유지합니다.
  * 외부 유료 에셋이나 무거운 3D 게임 엔진(Unity/OpenGL 셰이더 파일 등)에 의존하지 않고, 순수 **PyQt6 (`QPainter`, `QPainterPath`, `QLinearGradient`, `QRadialGradient`, `QPolygonF`, `QGraphicsDropShadowEffect`, QSS)**만으로 1280×720 60FPS 렌더링을 달성해야 합니다.

## 2. 첨부 레퍼런스 이미지 매핑 가이드 (Reference Image Mapping)

프롬프트에 함께 첨부된 2장의 이미지를 시각적 정답(Ground Truth)으로 삼아 각 화면을 구현합니다.

| 첨부 이미지 구분 | 대응하는 UI 모듈 ([app/ui/](https://www.google.com/search?q=https://github.com/didtjr5080/Rythm-Game/tree/main/app/ui)) | 핵심 시각 구성 요소 |
| :--- | :--- | :--- |
| **Image 1 (인게임 플레이 및 실시간 웹캠 HUD)** | [app/ui/game_widget.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/game_widget.py), [app/input/mediapipe_tracker.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/input/mediapipe_tracker.py) | • **중앙**: 3D 원근 프로스트 글래스 3레인 하이웨이(`LEFT`, `CENTER`, `RIGHT`), 3D 에메랄드·바이올렛 크리스탈 블록 노트, 판정선(`Y = 0.82`) 수면 파동(Water-Ripple) 동심원 이펙트, 상단/하단 `PERFECT` & `COMBO` 발광 타이포그래피<br>• **좌측 상단 글래스 카드**: `EMG DSP FILTER & THRESHOLD` 실시간 2중 파형 스플라인 그래프<br>• **좌측 하단 글래스 카드**: `EMG BIO-SIGNAL` 원형 다이얼 게이지(`% MVC ACTIVE` 표시)<br>• **우측 상단 글래스 카드**: `LIVE WEBCAM FEED & HAND TRACKING` 실시간 웹캠 PIP 영상 + 3레인 구역 분할 프레임(`LEFT \| CENTER \| RIGHT`) + 21-Point 네온 스켈레톤 오버레이<br>• **우측 하단 글래스 카드**: `LIVE CALIBRATION` 상태, `TIMING ERROR: -12ms` 정밀 오차 배지, `SCORE` 카운터 |
| **Image 2 (선곡·캘리브레이션·재활 분석 3단 대시보드)** | [app/ui/start_screen.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/start_screen.py), `song_select_screen.py`, `calibration_screen.py`, `result_screen.py` | • **상단 헤더**: `POST-GAME REHABILITATION ANALYTICS` (또는 로비/캘리브레이션 모드 타이틀) 및 세션 서브타이틀<br>• **좌측 글래스 패널 (`SONG & BEAT DSP ANALYSIS`)**: 오디오 스펙트럼 파형, 추출된 `BPM` 대형 타이포그래피, `CRYSTAL NOTE DENSITY` 프리뷰 트랙, 총 노트 수(`NOTES`) 및 초당 밀도(`DENSITY`) 표시<br>• **중앙 글래스 패널 (`NEURO-MOTOR PERFORMANCE REPORT`)**: 에메랄드·바이올렛 그라데이션 `RANK S+` 엠블럼, 원형 정확도 도넛 게이지(`96.8%`), `PERFECT` / `GOOD` / `MISS` 프로그레스 바 및 수치 요약<br>• **우측 글래스 패널 (`LIVE BIO-CALIBRATION`)**: 실시간 21-Point 손 관절 스켈레톤 뷰어(`HAND 1: ACTIVE`), 하단 `EMG THRESHOLD CALIBRATION DIAL` 원형 미터 및 센서 연결 상태 표시 |

## 3. 글로벌 디자인 시스템 및 컬러·타이포그래피 토큰 ([app/ui/theme.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/theme.py))

기존 [app/ui/theme.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/theme.py)의 단색 스타일시트(`APP_STYLE`)를 아래 **Glassmorphism Sonic Lab** 색상 팔레트와 QSS 헬퍼 함수로 전면 교체합니다.

### 3.1 컬러 팔레트 상수 정의

| 토큰 명칭 | HEX / RGBA 값 | 적용 대상 ([app/ui/theme.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/theme.py)) |
| :--- | :--- | :--- |
| `BG_DEEP_AURORA` | `#080B12` | 메인 윈도우 및 인게임 기본 배경색 |
| `AURORA_EMERALD_GLOW` | `rgba(16, 185, 129, 0.22)` | 좌측 배경 오로라 성운(`QRadialGradient`) 및 주 액센트 발광 |
| `AURORA_VIOLET_GLOW` | `rgba(139, 92, 246, 0.22)` | 우측 배경 오로라 성운(`QRadialGradient`) 및 보조 액센트 발광 |
| `GLASS_SURFACE_BG` | `rgba(18, 25, 38, 0.58)` | 플로팅 프로스트 글래스 카드 내부 채우기 색상 |
| `GLASS_SURFACE_HIGHLIGHT` | `rgba(255, 255, 255, 0.08)` | 글래스 카드 상단 대각선 반사광 그라데이션 시작점 |
| `GLASS_BORDER_LIGHT` | `rgba(255, 255, 255, 0.24)` | 글래스 카드 외곽선(`1.2px solid`) 기본 보더 |
| `GLASS_BORDER_ACTIVE` | `#10B981` | 활성화된 카드·웹캠 현재 레인 프레임(`LEFT \| CENTER \| RIGHT`) 네온 보더 |
| `CRYSTAL_EMERALD_CORE` | `#10B981` (상단면 `#6EE7B7`, 엣지 `#ECFDF5`) | 기본/중앙 레인 3D 크리스탈 노트 및 `PERFECT` 게이지 컬러 |
| `CRYSTAL_VIOLET_CORE` | `#8B5CF6` (상단면 `#C4B5FD`, 엣지 `#F5F3FF`) | 보조/우측 레인 3D 크리스탈 노트 및 DSP 서브 파형 컬러 |
| `TEXT_PRIMARY` | `#F8FAFC` | 메인 타이틀, 점수, BPM, 랭크 숫자 |
| `TEXT_SECONDARY` | `#94A3B8` | 카드 헤더 라벨(`EMG BIO-SIGNAL`, `TIMING ERROR` 등) |
| `STATUS_MISS_CORAL` | `#F43F5E` | `MISS` 판정 바 및 경고 표시 |

### 3.2 타이포그래피 및 커스텀 페인팅 헬퍼

* **폰트 패밀리 우선순위**: `'Orbitron'`, `'Rajdhani'`, `'Bahnschrift'`, `'Segoe UI Semibold'`, `'Malgun Gothic'`, `sans-serif` 순으로 폴백(Fallback) 체인을 구성합니다.
* **공용 글래스 카드 드로잉 함수 (`draw_frosted_glass_card`)**: [app/ui/theme.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/theme.py)에 `draw_frosted_glass_card(painter: QPainter, rect: QRectF, title: str = "", accent_color: QColor = None, tilt_deg: float = 0.0)` 유틸리티 함수를 구현하여 모든 화면에서 동일한 유리 질감(모서리 반경 `14px`, 상단→하단 반투명 그라데이션, 미세한 외곽선 하이라이트, 코너 브래킷 장식)을 재사용합니다.
* **공용 오로라 배경 드로잉 함수 (`draw_aurora_background`)**: `QPainter`로 `#080B12` 배경 위에 좌측 에메랄드 성운 곡선, 우측 바이올렛 성운 곡선, 미세한 스타더스트 파티클 점들을 렌더링하는 배경 함수를 작성합니다.

## 4. 인게임 화면 상세 구현 지침 ([app/ui/game_widget.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/game_widget.py) — Image 1 기준)

[app/ui/game_widget.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/game_widget.py)의 `paintEvent`를 **Image 1**의 레이아웃과 1:1로 매칭되도록 개편합니다.

### 4.1 중앙 3D 프로스트 글래스 하이웨이 및 크리스탈 노트 렌더링

1. **사다리꼴 원근 하이웨이 (3D Perspective Highway)**:
   * 화면 상단 소실점 부근(`Y_top = height * 0.30`, 폭 `width * 0.14`)에서 하단(`Y_bottom = height * 1.0`, 폭 `width * 0.64`)으로 넓어지는 사다리꼴 영역을 3개 레인(`LEFT`, `CENTER`, `RIGHT`)으로 균등 분할합니다.
   * 하이웨이 바닥면은 `QLinearGradient`를 사용해 상단은 투명(`rgba(16, 24, 39, 0.10)`), 하단은 반투명 프로스트 유리(`rgba(30, 41, 59, 0.65)`)로 채우고, 양쪽 끝 가드레일에 두께 `3px`의 에메랄드·바이올렛 발광 엣지를 그립니다.
   * 현재 손이 위치한 레인([app/input/input_fusion.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/input/input_fusion.py)의 `current_lane`) 바닥에는 은은한 에메랄드 수직 라이트 빔 그라데이션을 점등합니다.
2. **입체 3D 크리스탈 블록 노트 (`draw_crystal_note`)**:
   * [app/game/note.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/game/note.py)의 각 노트 진행률 $p \in [0, 1]$에 대해 원근 보간 공식 $p_{\text{persp}} = p^{1.65}$를 적용하여 상단에서는 작고 천천히, 판정선([app/config.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/config.py)의 `JUDGEMENT_LINE_Y_RATIO = 0.82`) 근처에서는 빠르고 입체감 있게 다가오도록 좌표를 변환합니다.
   * 각 노트는 단순 `drawRect`가 아니라 **윗면(Top Face 사다리꼴), 정면(Front Face 사각형), 측면(Side Bevel 다각형), 내부 대각선 크리스탈 굴절선(Facet Lines)**으로 구성된 3D 반투명 보석 블록으로 렌더링하며, 노트 뒤쪽에 위쪽으로 뻗는 반투명 빛 잔상(Vertical Motion Trail)을 함께 그립니다.
3. **판정선 및 수면 파동(Water-Ripple) 이펙트**:
   * `Y = height * 0.82` 지점에 좌측 에메랄드(`#10B981`)에서 우측 바이올렛(`#8B5CF6`)으로 이어지는 수평 레이저 판정선을 그립니다.
   * 노트 히트([app/game/judge.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/game/judge.py)의 `PERFECT` / `GOOD`) 또는 근육 수축(`emg_activated`) 발생 시, 해당 레인의 판정선 중심에서 타원형 동심원 파동(`RippleEffect`: 반경 확장 + 알파 감쇠, 3~4겹의 화이트·에메랄드 링)이 수면 물결처럼 퍼져 나가는 애니메이션 리스트를 매 프레임 업데이트합니다.
4. **판정 및 콤보 타이포그래피**:
   * 화면 상단 중앙(`Y = height * 0.16`)과 판정선 바로 위(`Y = height * 0.66`)에 자간이 넓은 지오메트릭 폰트로 `PERFECT` (화이트 코어 + 바이올렛/에메랄드 외곽 글로우)와 `152 COMBO` (`#10B981`)를 표시합니다.

### 4.2 좌측 플로팅 글래스 HUD 패널 (생체신호 DSP & 근활성도)

1. **좌측 상단 카드 — `EMG DSP FILTER & THRESHOLD`**:
   * 최근 120프레임의 원시(Raw) EMG 신호와 이동평균/RMS 포락선(Filtered Envelope) 값을 `collections.deque(maxlen=120)`에 저장합니다.
   * 글래스 카드 내부에 부드러운 3차 베지어 곡선(`QPainterPath.cubicTo`)으로 에메랄드 메인 파형과 바이올렛 서브 파형을 겹쳐 그리고, 파형 아래 영역을 반투명 오로라 그라데이션으로 채웁니다. 하단에는 눈금자(Tick Marks)를 배치합니다.
2. **좌측 하단 카드 — `EMG BIO-SIGNAL` 원형 다이얼**:
   * 원형 외부 눈금 링(60개 미세 각도 눈금)과 내부 진행 아크(`QPainter.drawArc`)를 에메랄드→바이올렛 그라데이션 펜으로 렌더링합니다.
   * 중앙에는 현재 임계값 대비 근수축 활성 비율을 계산하여 **`78%` (대형 에메랄드 텍스트)**와 **`MVC ACTIVE` (서브 라벨)**로 표시합니다.

### 4.3 우측 플로팅 글래스 HUD 패널 (실시간 웹캠 PIP & 정밀 판정 지표)

1. **우측 상단 카드 — `LIVE WEBCAM FEED & HAND TRACKING` (필수 핵심 요구사항)**:
   * [app/input/mediapipe_tracker.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/input/mediapipe_tracker.py)에서 캡처한 최신 OpenCV BGR 프레임(`numpy.ndarray`)과 MediaPipe 21개 손 랜드마크 좌표를 [app/ui/game_widget.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/game_widget.py)로 전달받습니다 (웹캠 미연결/폴백 시 다크 그리드 위에 시뮬레이션 손 스켈레톤이 움직이도록 안전하게 예외 처리).
   * OpenCV 프레임을 RGB `QImage`로 변환한 뒤, 우측 상단 글래스 카드 영역(`QRectF`) 안에 둥근 모서리 클리핑(`setClipPath`)으로 렌더링하고 가장자리에 어두운 비네팅 오버레이를 씌워 유리 패널과 자연스럽게 어우러지게 합니다.
   * **3레인 구역 프레임 오버레이**: 웹캠 영상 폭을 3등분(`0.333`, `0.666`)하여 현재 손이 위치한 구역(예: `CENTER`)에 밝은 에메랄드 네온 사각 프레임과 코너 타겟 브래킷(`[ ]`), 하단 `LEFT | CENTER | RIGHT` 라벨을 오버레이합니다.
   * **21-Point 네온 스켈레톤 오버레이**: 손바닥 기저부(0번 관절)에서 각 손가락 끝으로 이어지는 뼈대 연결선을 에메랄드(`#10B981`)와 바이올렛(`#8B5CF6`) 발광 선으로 그리고, 21개 관절 마디에 빛나는 원형 노드를 렌더링합니다.
   * **단축키 `V` 카메라 뷰 토글**: 기본값은 우측 상단 글래스 PIP 모드이며, 플레이 중 `V` 키를 누르면 하이웨이 배경 뒤에 웹캠 영상이 투명도 18%로 은은하게 함께 깔리는 AR 미러 배경 모드를 지원합니다.
2. **우측 하단 스탯 스택 카드 (3단 캡슐 카드)**:
   * **카드 1 (`LIVE CALIBRATION`)**: `HAND 1: MOTION` 및 `TRACKING INDICATOR: +0` (정규화 X좌표 및 센서 상태 텍스트).
   * **카드 2 (`TIMING ERROR`)**: [app/game/judge.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/game/judge.py)에서 마지막으로 판정된 노트의 시간 오차($\Delta t = t_{\text{input}} - t_{\text{note}}$)를 받아 **`TIMING ERROR: -12ms`** 형태로 실시간 표시합니다.
   * **카드 3 (`SCORE`)**: 현재 누적 점수([app/game/score.py](https://www.google.com/search?q=https://github.com/didtjr5080/Rythm-Game/blob/main/app/game/score.py))를 6자리 천 단위 콤마 포맷(**`098,450`**)으로 크게 렌더링합니다.

## 5. 선곡·캘리브레이션·재활 분석 통합 대시보드 구현 지침 (Image 2 기준)

[app/ui/start_screen.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/start_screen.py), `song_select_screen.py`, `calibration_screen.py`, `result_screen.py`는 **Image 2**의 **3열 프로스트 글래스 카드 레이아웃 (`QHBoxLayout` 3등분 패널)** 구조를 공유하여 시각적 통일성과 캡스톤 발표 시연 편의성을 높입니다.

| 패널 위치 | 패널 타이틀 | 주요 위젯 및 커스텀 렌더링 내용 | 연동 모듈 |
| :--- | :--- | :--- | :--- |
| **좌측 글래스 패널** | `SONG & BEAT DSP ANALYSIS` | • 상단: 선택된 음원의 오디오 엔벨로프 스펙트럼 파형(바이올렛 수직 바 + 에메랄드/화이트 스무스 곡선)<br>• 중단: 추출된 템포 **`128 BPM`** 대형 타이포그래피 및 비트 바 인디케이터, 곡 선택 콤보박스/리스트<br>• 하단 (`CRYSTAL NOTE DENSITY`): 수평 유리 라인 위에 떠 있는 미니 3D 크리스탈 조각 프리뷰 그래픽 + 하단 요약 수치(`NOTES: 412`, `DENSITY: 2.4/s`) | [app/ui/start_screen.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/start_screen.py), `app/audio/` |
| **중앙 글래스 패널** | `NEURO-MOTOR PERFORMANCE REPORT` | • 상단: `RANK` 라벨 및 에메랄드-바이올렛 그라데이션 + 스타 플레어(Star Flare) 효과가 적용된 초대형 **`S+`** (또는 `S`, `A`, `B`) 랭크 엠블럼<br>• 중단: 네온 에메랄드 이중 원형 도넛 게이지 및 중앙 정확도 퍼센트(**`96.8%`**)<br>• 하단: `PERFECT` (에메랄드 바), `GOOD` (라임 그린 바), `MISS` (코랄 레드 바) 수평 프로그레스 바와 우측 정렬 카운트 숫자, 하단 시연 시작/재시작 액션 버튼 | `app/ui/result_screen.py`, [app/game/score.py](https://www.google.com/search?q=https://github.com/didtjr5080/Rythm-Game/blob/main/app/game/score.py) |
| **우측 글래스 패널** | `LIVE BIO-CALIBRATION` | • 상단 (`HAND 1: ACTIVE`): 실시간 MediaPipe 21-Point 손 스켈레톤 및 반투명 손 실루엣 프리뷰 뷰어 + 코너 타겟 마커<br>• 하단 (`EMG THRESHOLD CALIBRATION DIAL`): `0 ~ 580` 눈금이 새겨진 원형 아크 다이얼과 임계값 조절 인터랙션(슬라이더 또는 마우스 드래그 연동), 우측 하단 `CONNECTED // CALIBRATED` 에메랄드 상태 LED 표시 | `app/ui/calibration_screen.py`, [app/input/input_fusion.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/input/input_fusion.py) |

## 6. 파일별 수정 체크리스트 및 구현 순서 (Step-by-Step Execution Plan for Codex)

Codex는 아래 순서대로 파일을 수정하고 검증을 수행합니다.

1. **Step 1 — [app/ui/theme.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/theme.py) 전면 개편**:
   * `Glassmorphism Sonic Lab` 컬러 상수, QSS 스타일시트(`APP_STYLE`), 그리고 `QPainter` 기반 공용 렌더링 헬퍼 함수(`draw_aurora_background`, `draw_frosted_glass_card`, `draw_circular_gauge`, `draw_crystal_note`, `draw_hand_skeleton_overlay`)를 구현합니다.
2. **Step 2 — [app/input/mediapipe_tracker.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/input/mediapipe_tracker.py) 및 [app/input/input_fusion.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/input/input_fusion.py) 데이터 노출 확장**:
   * 기존 반환값(`hand_visible`, `lane`, `emg_activated` 등)의 하위 호환성을 100% 유지하면서, UI 렌더링에 필요한 부가 텔레메트리 속성(`latest_frame_rgb`, `hand_landmarks_norm`, `raw_emg_value`, `filtered_emg_value`, `emg_mvc_ratio`, `last_timing_error_ms`)을 읽을 수 있도록 프로퍼티 또는 스냅샷 딕셔너리 필드를 추가합니다.
3. **Step 3 — [app/ui/game_widget.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/game_widget.py) 리팩토링 (Image 1 완벽 재현)**:
   * 3D 원근 글래스 하이웨이, 3D 크리스탈 블록 노트, 수면 파동(`RippleEffect`) 애니메이션, 좌측 2단 EMG 글래스 카드(파형 + 원형 다이얼), 우측 실시간 웹캠 PIP + 3레인 가이드 프레임 + 21-Point 스켈레톤 카드, 우측 하단 `TIMING ERROR` 및 `SCORE` 카드를 구현합니다.
4. **Step 4 — 로비·캘리브레이션·결과 화면 개편 (Image 2 완벽 재현)**:
   * [app/ui/start_screen.py](https://github.com/didtjr5080/Rythm-Game/blob/main/app/ui/start_screen.py), `song_select_screen.py`, `calibration_screen.py`, `result_screen.py`에 3단 프로스트 글래스 카드 레이아웃과 커스텀 그래프/다이얼 위젯을 적용합니다.
5. **Step 5 — 구동 및 검증 (Verification)**:
   * `python app/main.py` 실행 시 Import 오류나 QPainter 타입 에러(`float` vs `int` 좌표 문제 등 — PyQt6에서는 `QRectF`, `QPointF`를 엄격히 구분하여 사용)가 발생하지 않는지 확인합니다.
   * 하드웨어 EMG 센서나 웹캠이 연결되지 않은 환경(`USE_MOCK_EMG = True` 또는 카메라 미감지 상태)에서도 파형 시뮬레이션과 가상 손 스켈레톤 오버레이가 정상 작동하여 캡스톤 심사 현장에서 언제든 끊김 없이 시연 가능한지 검증합니다.
