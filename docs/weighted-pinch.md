# Leap 70% + EMG 30% 핀치 점수

EXTRACTED: 이 기능은 이후 사용자 요청으로 제거했다. 최신 핀치는 [Leap 전용](pinch-leap-only.md)이며 아래는 과거 구현 기록이다.

EXTRACTED: 일반 핀치 게임은 두 센서의 선택이 같아야 한다는 기존 조건 대신 다섯 자세(NONE, INDEX, MIDDLE, RING, PINKY)의 점수를 합산한다.

```text
fused[label] = 0.70 * leap[label] + 0.30 * emg[label]
```

EXTRACTED: 각 센서 점수는 합이 1인 참고 점수다. 실제 통계적으로 보정된 확률이나 임상 정확도가 아니다. 게임 HUD의 L/E/F는 각각 Leap, EMG, 합산 점수이며 백분율로 표시한다. 최종 선택도 FUSED 항목으로 표시한다.

## 점수와 입력

EXTRACTED: Leap은 보정된 손가락별 임계값에 대한 거리 비율로 핀치 점수를 만든다. 각 손가락 로짓은 `4*(1-distance_ratio/threshold)`, NONE 로짓은 0이다. softmax로 정규화한 뒤 SDK의 손 추적 confidence가 낮으면 균등 점수 쪽으로 낮춘다. 기존 Leap 분류의 확정 레인이 없더라도 유효한 손과 좌표가 있으면 점수 합산으로 판단할 수 있다. 손 추적이 끊기면 입력하지 않는다.

EXTRACTED: EMG는 기존 8채널 RMS 보정 벡터의 log 변환·자세별 중심·정규화 거리를 사용한다. `-0.5 * distance**2`를 softmax로 변환하므로 비슷한 자세에는 점수가 나뉜다. 보정 범위에서 크게 벗어난 벡터는 어느 자세도 우선하지 않는 20%씩의 중립 점수를 준다. 다른 장치 ID나 잘못된 벡터는 유효 점수가 아니다.

EXTRACTED: 합산 1위가 NONE이면 레인을 선택하지 않는다. 핀치를 선택하려면 합산 점수 60% 이상이고, 2위와의 차이가 15%p 이상이어야 한다. Leap 손 추적·EMG 신선도·보정 모델도 유효해야 한다. EMG 수신 중단 시 Leap 100%로 자동 전환하지 않는다. 숫자는 구현의 초기 기본값이며 실제 착용 성능으로 검증된 값이 아니다.

EXTRACTED: 예를 들어 Leap이 INDEX 100%, EMG가 MIDDLE 100%이면 합산은 INDEX 70%, MIDDLE 30%로 INDEX 입력이 가능하다. Leap이 INDEX 48%, MIDDLE 48%, NONE 4%이고 EMG가 MIDDLE 100%이면 MIDDLE은 63.6%가 되어 EMG가 모호한 Leap 선택을 보조한다.

## 보정 및 기존 모드

EXTRACTED: 매 게임 시작 전 열린 손과 네 핀치의 새 보정은 유지한다. 일반 모드는 유효 샘플·장치·Leap 임계값 검증과 저장을 요구하지만, EMG 클래스 중심 간 최소 거리 및 보정 샘플 인정률 80% 조건은 요구하지 않는다. 따라서 INDEX/MIDDLE의 EMG 패턴 유사성만으로 게임 시작을 막지 않는다. EMG가 다섯 클래스 모두 같은 패턴이면 점수는 각각 20%다.

EXTRACTED: armband 단독 테스트는 Leap 보조가 없으므로 기존 엄격한 패턴 분리 검사와 단독 분류를 유지한다. 근전도 1레인 게임의 3초 안정값 측정·+0.01 입력, 핀치의 기존 타이밍·4레인·연속 MISS 10회 종료 규칙도 유지한다.

EXTRACTED: 세션 기록에는 `leap_scores`, `emg_scores`, `fused_scores`를 추가하고 일반 핀치 입력 출처를 `leap70_emg30`으로 기록한다. 기존 게임 모드·채보 형식은 변경하지 않는다.

## 검증 및 배포

EXTRACTED: 관련 소스 검사 81개 통과. 새 `docs/check_weighted_pinch.py`는 Leap 점수 정규화, 정확한 70/30 계산, 센서 불일치 시 강한 Leap 입력 유지, EMG를 통한 모호한 Leap 선택 보조, NONE·낮은 점수·누락 입력 보류, 일반 모드의 중첩 패턴 보정 허용과 단독 모드의 거부를 검사한다. 기존 실제 GameWidget 검사에서도 EMG 불일치 시 Leap 우선 득점·점수 HUD 렌더링을 검증했다.

AMBIGUOUS: 실제 착용자의 새 합산 점수와 판정 성능은 아직 검증하지 않았다. 기존 스크린샷의 보정 원본 벡터는 없어 당시 데이터 재현 검사는 하지 못했다.

새 실행 폴더: `dist_windows_weighted_pinch_2026.11.18/EMG-Motion-Rhythm-No-Bandpass`. `_internal`을 포함한 폴더 전체로 실행한다. 기존 배포 폴더는 보존한다.

EXTRACTED: 새 EXE 자체 검사 17항목 통과(`ok=true`, `pinch_requires_sensor_agreement=false`, `pinch_fusion_weights={leap:0.7, emg:0.3}`). 보고서는 배포 폴더의 `self-test.json` 및 `release/self-test-weighted-pinch-2026.11.18.json`이다. 기존 설정·Leap 프로필을 복사하고 SDK DLL 해시 일치를 확인했다. 실제 착용 검사는 대신하지 않는다. 이전 실행 중인 게임을 종료하고 새 EXE에서 armband 단독 체크를 해제한 일반 핀치 모드를 선택한다.

변경 소스: `app/input/weighted_pinch.py`, `pinch_intent.py`, `leap_tracker.py`, `input_fusion.py`, `app/ui/leap_calibration_dialog.py`, `game_selection_screen.py`, `game_widget.py`, `app/analytics/session_logger.py`, `app/diagnostics.py` 및 관련 검사.

[Mermaid 흐름](../diagrams/weighted-pinch.md)은 Mermaid 지원 Markdown 미리보기에서 연다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 출력은 갱신하지 않았다.
