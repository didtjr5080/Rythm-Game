# Leap + armband 핀치 의도 보정

EXTRACTED: 핀치의 armband 연동은 이후 사용자 요청으로 전부 제거했다. 현재 동작은 [Leap 전용 핀치](pinch-leap-only.md)를 참고한다. 아래는 과거 점검·구현 기록이다.

EXTRACTED: 최신 일반 모드는 [Leap 70% + EMG 30% 가중 점수](weighted-pinch.md)를 사용한다. 아래 두 센서 일치 필수 및 EMG 분리 실패 시 시작 차단 규칙은 이전 버전 기록이다. armband 단독 테스트의 엄격 검사는 유지한다.

EXTRACTED: 재부팅으로 COM4가 복구된 뒤 제공된 화면의 NONE/INDEX/MIDDLE/RING/PINKY 샘플 개수는 각각 52/53/53/26/41쌍으로 모두 최소 25쌍을 넘었다. `Armband NONE: patterns overlap or vary too much`는 코드상 NONE 보정 샘플 인정률이 80% 미만일 때 발생하는 오류다. 단순 샘플 수 부족과 구분한다. 현재 선택이 PINKY여도 오류 대상은 NONE이므로 열린 손을 선택해 재측정할 수 있다. 다른 동작 데이터는 해당 동작만 재측정할 때 유지된다.

AMBIGUOUS: 해당 보정의 원본 8채널 벡터는 전달되지 않아 어떤 자세와 겹치는지, 움직임 또는 착용 상태가 원인인지는 확정할 수 없다. 화면은 Leap + armband 보정 모드이며, 단독 테스트를 원하면 취소 후 게임 선택의 armband만 사용 체크박스로 진입한다. 단독 모드도 동일한 패턴 분리 검사를 사용하므로 모드 변경이 이 오류의 해결을 보장하지 않는다. 이번 점검에서는 코드·판정 기준·EXE를 바꾸지 않았다.

EXTRACTED: 테스트용 [armband 단독 입력](armband-only-test.md)을 게임 선택의 체크박스로 선택할 수 있다. 아래 규칙은 기본 두 센서 모드에 적용한다.

EXTRACTED: 핀치 게임은 이제 Leap Motion과 OYMotion armband를 함께 사용한다. 사용자가 선택한 규칙은 **Leap이 선택한 핀치와 armband가 분류한 핀치가 같을 때만 입력 인정**이다. 근전도 리듬·유지 모드의 시작 전 3초 안정값 측정과 +0.01 규칙은 별도로 유지한다.

## 게임 시작 전

EXTRACTED: Settings에서 OYMotion과 해당 USB 동글 COM 포트를 선택한다. armband는 Leap이 추적하는 오른손의 팔에 착용한다. 핀치 모드 선택 및 재시도마다 열린 손(NONE), 엄지+검지(INDEX), 엄지+중지(MIDDLE), 엄지+약지(RING), 엄지+소지(PINKY)를 새로 측정한다. 각 동작은 1초 준비 후 3초 유지한다.

EXTRACTED: 보정 창은 Leap 손 측정과 armband의 8채널 RMS 벡터를 함께 모은다. 두 센서 모두 유효하고 새 샘플일 때만 쌍으로 기록한다. 같은 Leap 프레임이나 armband 특징을 중복 집계하지 않는다. armband 미수신 시 진행 중인 동작의 측정을 비우고 재측정을 안내한다. 장치 교체나 특징 순번 초기화 시 기존 수집 데이터를 비운다. 다섯 동작 각각 최소 25쌍이 필요하다.

EXTRACTED: armband 연결에는 공유 `EMGSession`을 사용한다. 보정 창을 닫으면 해당 lease를 닫고, 게임은 같은 물리 수신 스트림을 새 lease로 이용한다. 핀치 보정에 Demo/SPACE나 Legacy 단일 채널 신호를 대신 사용하지 않는다. armband 미연결 상태에서 기존 Leap 보정값만으로 게임을 시작할 수 없다.

## 의도 분류와 판정

EXTRACTED: `app/input/pinch_intent.py`는 다섯 자세의 8채널 RMS를 `log(1+RMS)`로 변환하고 자세별 중심과 자세 내 변동을 계산한다. 채널별 공통 변동으로 거리를 정규화한 최근접 중심 분류를 사용한다. 중심 간 거리가 너무 작거나, 학습 샘플 중 해당 자세로 인정되는 비율이 어느 클래스에서든 80% 미만이면 보정 실패로 처리한다. 이 비율은 보정 데이터의 분리 여부 검사이며 실제 인식 정확도가 아니다.

EXTRACTED: 실시간 입력은 가장 가까운 중심의 허용 반경 안에 있고, 두 번째 후보보다 상대 거리 차이가 15% 이상일 때만 해당 자세로 분류한다. 열린 손은 NONE이며 어떤 레인도 선택하지 않는다. 다른 장치 ID, 범위를 벗어난 값, 불확실한 패턴은 분류하지 않는다. 임계값은 구현상의 기본값이며 개인별 임상 성능을 검증한 값은 아니다.

EXTRACTED: `InputFusion`은 Leap의 레인과 armband의 INDEX/MIDDLE/RING/PINKY를 비교한다. 일치하고 손이 보이며 armband 신호가 신선할 때만 레인을 전달한다. 불일치·미보정·불확실·수신 중단 시 레인을 비운다. 펼친 손을 중간에 거치지 않고 핀치를 바꾸어도 두 센서가 새 자세로 일치하면 인정한다. armband 특징은 기존 100ms RMS 창, 약 20ms 갱신을 사용하므로 전환 시 창에 따른 지연이 있다.

EXTRACTED: armband 분류 모델은 이번 게임을 위한 메모리에만 유지하고 재시도 시 다시 만든다. Leap 임계값은 기존 로컬 프로필에 저장한다. 세션 기록에는 Leap 핀치, armband 의도, 일치 여부를 추가했다. 게임 HUD에는 armband 분류와 MATCH/대기 상태를 표시한다. 핀치의 10회 연속 MISS 종료 규칙은 유지한다.

## 검증과 사용 범위

EXTRACTED: 관련 소스 검사 67개 통과. `docs/check_pinch_intent.py`는 합성 8채널 데이터로 다섯 자세·직접 전환, 패턴 중첩 거부, 장치 불일치·이상값·불확실 패턴 거부, 네 레인 일치 시 득점, 불일치 시 MISS, 신호 소실, 세션 교체, 샘플 중복 방지 및 보정 취소 시 연결 해제를 검증한다. 실제 GameWidget에서도 센서 일치 득점·불일치 미득점과 Demo 설정에 관계없이 실장치 공유 스트림을 선택하는지 검증한다.

AMBIGUOUS: 실제 착용자의 열린 손과 네 핀치 분류 정확도는 아직 측정하지 않았다. 기존 실장치 8채널 수신 확인은 자세 분류 검증과 다르다. 특히 패턴이 비슷한 자세는 보정 단계에서 거부될 수 있다. 실제 Leap·armband 동시 보정 및 게임 전환, 장시간 착용 중 변화는 TODO다.

EXTRACTED: 새 실행 폴더는 `dist_windows_pinch_armband_2026.11.18/EMG-Motion-Rhythm-No-Bandpass`다. `_internal`을 포함한 폴더 전체를 사용한다. 이전 배포 폴더는 유지한다.

EXTRACTED: 새 EXE 자체 검사 16항목 통과(`ok=true`, `pinch_requires_sensor_agreement=true`). 배포 SDK DLL의 원본 해시 일치와 기존 설정·Leap 프로필 복사도 확인했다. 보고서는 배포 폴더의 `self-test.json` 및 `release/self-test-pinch-armband-2026.11.18.json`이다. EXE 자체 검사도 합성 신호를 사용하며 실제 착용자의 분류 정확도는 검증하지 않는다.

관련 소스: `app/input/pinch_intent.py`, `oymotion_activity.py`, `oymotion_reader.py`, `emg_session.py`, `input_fusion.py`, `app/ui/leap_calibration_dialog.py`, `main_window.py`, `game_widget.py`, `game_selection_screen.py`, `settings_screen.py`, `app/analytics/session_logger.py`, `app/diagnostics.py`.

[Mermaid 흐름](../diagrams/pinch-armband-intent.md)은 Mermaid 지원 Markdown 미리보기에서 확인한다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 출력은 자동 갱신하지 않았다.
