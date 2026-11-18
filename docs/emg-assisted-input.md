# EMG 보정·게임 값 일치와 입력 인정 범위 확대

EXTRACTED: 이 문서는 이전 ON/OFF 보정 방식의 기록이다. 최신 요청에서는 보정 UI와 게임의 기존 임계값 사용을 제외하고 [시작 전 3초 안정 기준 +0.01](emg-rest-baseline.md)을 적용한다. 공유 EMG 연결·필터는 유지한다.

EXTRACTED: 보정·메뉴·게임 화면이 EMG 포트와 필터를 공유하도록 변경했다. 근전도 모드만 박자 허용 구간과 긴 노트의 짧은 활성 저하 허용 시간을 넓혔다. 핀치 판정과 채보 생성 규칙은 유지한다.

## 확인한 구조와 변경

EXTRACTED: 기존에는 Settings의 EMG 보정, 메인 입력 표시, 별도 보정 화면, 게임이 각자 SerialEMGReader를 만들고 페이지를 떠날 때 닫았다. 새 리더는 필터 상태를 새로 시작하고 시리얼 포트를 다시 연다. 보정 화면의 표시도 정수이고 게임은 소수 두 자리였다.

AMBIGUOUS: 사용자의 실제 값 차이를 하드웨어로 재현하지는 못했다. 포트 재연결·필터 초기화와 저장하지 않은 보정값은 확인된 차이 발생 가능 경로이며, 전극·자세·수축 정도 등에 따른 실제 신호 변동을 이번 변경으로 제거한다고 단정하지 않는다.

EXTRACTED: MainWindow가 EMGSession을 소유한다. 첫 연결 후 10ms QTimer가 동일 리더를 계속 읽고, 각 화면은 EMGLease로 같은 최신 처리값을 읽는다. 화면을 닫아도 포트와 필터를 닫지 않는다. 장치·신호 종류·baudrate가 바뀌거나 앱이 종료될 때 연결을 교체/종료한다. 이미 연결한 동일 장치의 USB 식별자를 보정 저장 시 확정해도 포트를 다시 열지 않는다.

EXTRACTED: 각 lease는 새 측정 패킷을 자신의 보정 수집에 한 번씩만 전달한다. 화면 갱신 속도가 달라도 같은 패킷을 반복 수집하지 않는다. 실제 EMG 필터·프로토콜·ON/OFF 감지 코드는 변경하지 않았다. 공유 상태는 메모리이며 서버나 데이터베이스를 추가하지 않았다.

EXTRACTED: 보정 화면도 ACTIVITY 값을 소수 두 자리로 표시한다. 게임은 ON/OFF와 박자·활성 저하 허용값을 함께 표시한다. 표시하는 값은 동일한 ActivityFilter 처리값이며 원시 RAW 값과 섞지 않는다. 서로 다른 시각의 화면 숫자가 자연스러운 신호 변화까지 포함해 항상 동일해야 한다는 의미는 아니다.

## 넓어진 근전도 판정 범위

| 항목 | 이전 | 현재 |
| --- | --- | --- |
| EMG 박자 인정 | 예정 시각 ±100ms | ±350ms |
| EMG PERFECT | 시작 오차 50ms 이내 | 150ms 이내 |
| 긴 노트의 짧은 근활성 저하 | 즉시 MISS | 400ms 이내 회복 허용 |
| 새 자동 보정 ON | 안정→수축 차이의 60% | 35% |
| 새 자동 보정 OFF | 안정→수축 차이의 20% | 10% |

EXTRACTED: 긴 노트에서 활성 저하가 시작된 뒤 400ms 이내에 다시 활성화되면 같은 노트를 이어간다. 비활성이 400ms를 넘거나 회복이 더 늦으면 MISS이다. 꼬리에서 잠깐 비활성이면 즉시 성공을 주지 않고 허용 구간 안에 회복한 경우에만 완료한다. 음악이 먼저 끝나도 마지막 유지 노트의 짧은 회복 대기는 처리한다.

EXTRACTED: 장치 분리·오래된 센서 데이터는 활성 저하 여유와 별개로 실패 처리한다. 실제 리더의 약 150ms 데이터 신선도 검사와 250ms 초과 게임 관찰 공백 차단을 유지한다. 입력이 없거나 끊긴 상태를 긴 노트 성공으로 바꾸지 않는다. 짧은 노트는 여전히 새로운 수축 시작이 필요하다.

EXTRACTED: 새 자동 보정은 기존 안정 상태·3회 수축·3회 회복 중앙값 계산을 사용하고 비율만 바꿨다. 안정값 R, 수축값 A에 대해 ON=`R+0.35*(A-R)`, OFF=`R+0.10*(A-R)`이다. 수축 시 증가하는 신호와 감소하는 신호에 모두 적용된다.

EXTRACTED: 자동 보정이 성공하면 장치 선택·신호 유형·ON/OFF 값을 즉시 설정 파일에 저장한다. 게임은 같은 세션과 저장값을 사용한다. 저장 실패는 화면에 표시하고 현재 연결에만 적용된 사실을 알린다. 기존 개인의 저장 임계값을 임의로 다시 계산하지 않았으므로 새 ON/OFF 비율을 사용하려면 자동 보정을 다시 해야 한다.

## 사용 방법

1. 새 EXE에서 Settings → Connect / Test EMG로 ACTIVITY와 장치 연결을 확인한다.
2. **1. 안정 상태 측정** 후 **2. 3회 반복 수축 / 임계값 자동 보정**을 진행한다.
3. **자동 저장 완료**를 확인하고 게임 선택 → 근전도 게임으로 이동한다.
4. 게임의 ON/OFF가 보정 결과와 같은지 확인한다. 다른 환경 설정 변경은 기존 Save 버튼으로 저장한다.

## 검증과 TODO

EXTRACTED: 새 실행 파일은 `dist_windows_emg_assisted_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. `_internal`을 포함한 폴더 전체를 사용한다. 이전 두 모드 빌드의 설정·개인별 핀치 보정 파일 2개를 복사했다. 기존 EMG 임계값을 자동으로 낮추지는 않았다. 새 자동 보정으로 개인의 측정값에 맞춰 다시 계산한다. 이전 실행 폴더는 유지했다.

```powershell
$env:EMG_NO_BANDPASS_BUILD='1'
.venv311/Scripts/python.exe -m PyInstaller --noconfirm --distpath dist_windows_emg_assisted_2026.11.18 --workpath build/leap_only_2026.11.18 EMG-Motion-Rhythm.spec
```

```powershell
.venv311/Scripts/python.exe -m unittest docs.check_emg_assistance docs.check_game_modes docs.check_pinch_judgement docs.check_pinch_switch docs.check_leap_calibration docs.check_lane_transition docs.check_leap_input -v
```

EXTRACTED: 소스 검사 40개 통과. 모의 시리얼에서 실제 Settings 보정 성공→자동 저장→GameWidget 전환을 실행하여 포트 생성 1회, 동일 필터·ON/OFF·처리값 재사용을 확인했다. USB 식별자 저장 시 재연결 방지, 신호 종류 변경 시 연결 교체, 패킷 중복 수집 방지, 양방향 약한 수축 보정식, 넓어진 시각 경계, 400ms 활성 회복, 실제 신호 손실 차단, 음악 종료 후 마지막 회복 구간도 검사했다. 기존 두 게임 모드·핀치 회귀 검사도 통과했다.

EXTRACTED: 새 EXE 자체 검사 14항목 통과(`ok=true`, `emg_judge_window_ms=350`, `emg_hold_dropout_ms=400`). 공유 EMG 상태 재사용, 완화된 보정 계산, 짧은 활성 저하 후 긴 노트 회복과 기존 두 모드 동작을 확인했다. 보고서는 `release/self-test-emg-assisted-2026.11.18.json`과 실행 폴더의 `self-test.json`에 있다. 실행 폴더에 `README-EMG-ASSISTED.txt`도 포함했다.

AMBIGUOUS: 위 수치는 편마비 사용을 고려한 소프트웨어 기본 허용값이다. 개인별 적합성이나 임상 효과를 검증한 값은 아니다. 실제 장치에서 보정→게임 값의 연속성과 사용자의 힘·노이즈 수준에 맞는 인식 여부를 확인해야 한다.

[Mermaid 입력·보정 흐름](../diagrams/emg-assisted-input.md)은 Mermaid 지원 Markdown 미리보기로 연다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 보고서는 자동 갱신하지 않았다.
