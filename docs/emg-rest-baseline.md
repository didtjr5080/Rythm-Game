# EMG 시작 전 3초 안정 측정 / +0.01 입력

EXTRACTED: 이 문서는 이전 평균+0.01 규칙 기록이다. 현재2026.11.18.5는 **3.0초 기록의 최저값 이상이면 신전**이며 [현재 기준·검증](emg-minimum-baseline.md)을 우선한다.

EXTRACTED: 수동 근전도 보정·3회 수축 보정 버튼과 임계값 조절 UI를 제외했다. 근전도 게임을 시작할 때마다 음악과 노트를 멈춘 상태에서 3초간 가만히 있는 안정값을 측정한다. 측정 완료 후 음악과 게임 시간을 새로 시작한다. 핀치 개인별 보정 기능은 유지한다.

EXTRACTED: 실제 새 EMG 패킷들의 평균을 안정 기준으로 사용한다. 기준과 현재 ACTIVITY를 소수 둘째 자리 단위로 반올림한 뒤 정수 0.01 단위로 비교한다. `현재 값 >= 안정 기준 + 0.01`이면 활성이다. 예: 안정 185.03 → 185.03은 REST, 185.04부터 ACTIVE. 부동소수점 덧셈 오차로 0.01 경계가 누락되지 않도록 정수 단위로 비교한다.

EXTRACTED: 기존 저장 ON/OFF, 감소형 신호, 휴식 후 재무장 상태와 이전 리더의 활성 bool은 게임 입력 결정에 사용하지 않는다. 동일한 필터 처리 ACTIVITY를 읽되 근전도 GameWidget에서 시작 전 기준과 직접 비교한다. 기준은 매 게임 새로 측정하며 파일에 고정 임계값으로 저장하지 않는다.

EXTRACTED: 측정 도중 센서 데이터가 끊기면 누적값과 3초 타이머를 초기화한다. 유효한 새 데이터가 들어온 뒤 연속 3초를 측정한다. 장치가 없으면 대기하고 자동 진행하지 않는다. 측정 중 취소하면 음악을 시작하지 않는다. 명시적 데모 모드는 같은 3초 흐름을 모의 값으로 수행한다.

EXTRACTED: 게임 HUD에는 기존 ON/OFF 대신 `REST 기준 / ON 기준+0.01`을 표시한다. 박자 ±350ms, 긴 노트의 400ms 짧은 활성 저하 회복, 신규 수축 시작 판정과 센서 데이터 신선도 검사는 유지한다. 결과에는 이번 게임의 `emg_rest_baseline`과 `emg_activation_delta=0.01`을 기록한다.

EXTRACTED: Settings에는 EMG 장치·신호 선택과 연결 테스트만 유지한다. 예전 근전도 보정 화면으로 가던 메인 버튼을 제거하고 이전 화면 진입 경로도 설정 화면으로 연결한다. 이전 근전도 보정 함수·화면의 일부 소스는 과거 호환 기록으로 남지만 현재 UI에서 실행하지 않는다. 이전 저장 임계값 파일은 덮어쓰거나 삭제하지 않으며 게임에서 무시한다.

## 검증

EXTRACTED: 새 실행 파일은 `dist_windows_emg_rest_001_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. `_internal`을 포함한 폴더 전체를 사용한다. 기존 앱을 닫은 뒤 새 EXE를 실행하면 같은 COM 포트가 다른 앱에 점유되는 일을 피할 수 있다. 기존 장치·신호 설정과 핀치 보정은 보존하고 기존 근전도 ON/OFF는 게임에서 무시한다.

```powershell
$env:EMG_NO_BANDPASS_BUILD='1'
.venv311/Scripts/python.exe -m PyInstaller --noconfirm --distpath dist_windows_emg_rest_001_2026.11.18 --workpath build/leap_only_2026.11.18 EMG-Motion-Rhythm.spec
```

```powershell
.venv311/Scripts/python.exe -m unittest docs.check_rest_baseline docs.check_emg_assistance docs.check_game_modes docs.check_pinch_judgement docs.check_pinch_switch docs.check_leap_calibration docs.check_lane_transition docs.check_leap_input -v
```

EXTRACTED: 소스 검사 45개 통과. 정확한 3초 경계, 0.01 활성 경계, 새 게임의 새 기준, 신호 손실 시 재측정, 측정 전 음악·득점 차단, 기존 감소형 활성 False를 무시한 새 기준 득점, 수동 보정 UI 제거를 검사했다. 기존 두 모드·긴 노트·핀치 기능 검사도 통과했다.

EXTRACTED: 최종 EXE 자체 검사 14항목 통과(`ok=true`, `emg_rest_measurement_seconds=3`, `emg_activation_delta=0.01`). 보고서는 `release/self-test-emg-rest-001-final-2026.11.18.json`과 실행 폴더의 `self-test.json`에 있다. 실행 폴더에 `README-REST-001.txt`를 포함하고 이전 설정·핀치 보정 2개 파일을 보존했다. 메인·결과 화면의 이전 EMG 임계값/보정 표시도 자동 3초 안정 측정 안내로 변경했다.

AMBIGUOUS: 실제 센서·사용자 환경에서 3초 안정 측정과 +0.01 인식을 확인해야 한다. 작은 잡음도 표시값을 0.01 올리면 요청한 규칙에 따라 활성으로 인정된다. 별도의 추가 차이값·노이즈 여유·개인별 임계값을 덧붙이지 않았다.

[Mermaid](../diagrams/emg-rest-baseline.md)는 Mermaid 지원 Markdown 미리보기에서 연다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 보고서는 자동 갱신하지 않았다.
