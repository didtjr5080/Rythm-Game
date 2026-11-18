# Leap Motion 개인별 핀치 보정

EXTRACTED: 개인 보정·직접 전환은 최신 [EMG 없는 핀치 유지 판정](pinch-hold-scoring.md)에도 적용한다. 아래 EMG 판정 유지 설명은 변경 전 기록이다.

EXTRACTED: 설정 화면의 **Leap Motion 개인별 핀치 보정** 버튼에서 열린 손과 오른손 엄지+검지·중지·약지·소지를 각각 측정한다. 웹캠은 사용하지 않는다. 게임의 EMG 판정과 MIDDLE → RING 노트 제약은 유지한다.

## 사용 순서

1. Settings → **Leap Motion 개인별 핀치 보정**을 연다.
2. 개인 이름을 입력한다. 기존 보정을 선택하려면 저장된 이름을 선택하고 **선택한 기존 보정 사용**을 누른다.
3. 열린 손을 선택하고 **선택 동작 측정**을 누른다. 1초 준비 후 오른손을 3초 유지한다.
4. 같은 방식으로 엄지+검지, 엄지+중지, 엄지+약지, 엄지+소지를 측정한다. 프레임이 충분하면 다음 동작이 자동 선택된다.
5. 다섯 측정이 끝나면 **보정 저장 및 적용**을 누른다. 선택된 개인 보정은 다음 게임과 다음 앱 실행부터 사용된다.
6. 보정을 사용하지 않으려면 **기본 임계값 사용**을 누른다. 저장된 개인별 값은 유지한다.

EXTRACTED: 같은 이름으로 저장하면 해당 이름의 값이 교체된다. 다른 이름의 보정은 유지한다. 이름을 바꾸면 현재 창의 미저장 측정값을 비운다. 측정 도중 닫으면 저장하지 않고 Leap 작업 스레드를 종료한다.

## 계산과 저장

EXTRACTED: `Orion_4_1_Pinch_Lab_Fix_v3/leap_pinch_lab.py`의 Calibrator 방식을 따라 손바닥 너비로 정규화한 엄지–손가락 끝 거리의 중앙값을 사용한다. 각 동작은 서로 다른 유효 추적 프레임 25개 이상이 필요하다. 같은 프레임을 반복 수집하지 않으며, 250ms 이상 오래된 추적 결과를 받지 않는다. 측정 중 손 ID가 바뀌면 해당 동작의 누적 측정을 비운다.

EXTRACTED: 각 손가락의 열린 손 중앙값을 O, 핀치 중앙값을 P라고 할 때 `P + 0.40 × (O − P)`를 계산하고 0.12~0.70 범위로 제한한다. `O − P < 0.08`이면 두 동작을 구별하기 어렵다고 보고 저장하지 않는다. 후보 분리와 최초 진입·해제의 약 90ms 안정화는 유지한다. 이후 연속 전환 수정에서는 명확한 새 핀치가 나오면 기존 핀치 해제나 추가 안정화 대기를 요구하지 않는다.

## 손을 펼치지 않는 연속 핀치 전환

EXTRACTED: 기존 분류기는 이전 손가락 거리가 해제 임계값 이내이면 새 핀치 후보를 무조건 이전 핀치로 덮어썼다. 개인 보정으로 해제 범위가 넓어진 경우에도 이전 핀치가 붙잡히는 조건을 모의 좌표로 재현했다.

EXTRACTED: 새 후보가 개인별 핀치 임계값과 후보 간 거리 차이 0.065를 만족하면 해당 프레임에서 새 핀치로 전환한다. 열린 손 중간 단계가 필요 없고 전환용 90ms 대기도 없다. 두 손가락이 비슷하게 가까워 후보가 모호하면 기존 핀치를 해제 히스테리시스로 유지한다. 최초 핀치 진입·핀치 해제·추적 손실의 처리 방식은 유지한다.

EXTRACTED: 기본 임계값, 동일한 개인 임계값, 손가락마다 다른 개인 임계값에서 각각 12방향, 총 36개 직접 전환을 검사했다. 모호한 후보의 기존 선택 유지, 최초 진입·해제·추적 손실도 확인했다. 전체 소스 검사 15개 통과. 게임의 MIDDLE → RING 노트 생성 금지와 손 입력 전환은 별개다.

EXTRACTED: 새 EXE는 `dist_windows_leap_direct_pinch_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. 이전 `dist_windows_leap_personal_calibration_2026.11.18`의 개인별 보정 파일을 유효성 확인 후 새 폴더의 동일한 상대 위치로 복사했다. 이전 폴더와 파일은 유지했다. 기존 보정값을 다시 측정할 필요 없이 사용할 수 있다.

EXTRACTED: 새 EXE 자체 검사 11항목 통과(`ok=true`). 보정값 적용 상태에서 12방향 즉시 전환을 검사했다. 보고서는 `release/self-test-leap-direct-pinch-2026.11.18.json`과 실행 폴더의 `self-test.json`에 있다. 실제 사용자 손의 연속 전환은 별도 확인이 필요하다.

```powershell
.venv311/Scripts/python.exe -m unittest docs.check_pinch_switch docs.check_leap_calibration docs.check_lane_transition docs.check_leap_input -v
```

EXTRACTED: 프로필은 기존 settings 파일과 같은 디렉터리의 `leap_calibration.json`에 저장한다. 소스 실행은 `app/data/leap_calibration.json`, EXE는 `_internal/app/data/leap_calibration.json`이다. 원시 손 좌표와 수집 프레임은 저장하지 않으며 개인 이름, 네 임계값, 선택된 개인 이름만 저장한다. 같은 디렉터리의 임시 파일을 완성한 후 교체한다.

EXTRACTED: 누락·비정상 임계값과 잘못된 파일 구조는 허용하지 않는다. 손상된 파일을 보정 창에서 덮어쓰지 않는다. 게임은 잘못된 개인 보정 파일을 읽으면 오류를 표시하고 기본 임계값을 사용한다. 개인 보정 파일이 없으면 기본값 0.36을 사용한다.

## 검증과 TODO

EXTRACTED: 새 실행 파일은 `dist_windows_leap_personal_calibration_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. 이전 빌드 폴더는 유지한다. `_internal`을 포함한 전체 폴더를 사용한다.

```powershell
$env:EMG_NO_BANDPASS_BUILD='1'
.venv311/Scripts/python.exe -m PyInstaller --noconfirm --distpath dist_windows_leap_personal_calibration_2026.11.18 --workpath build/leap_only_2026.11.18 EMG-Motion-Rhythm.spec
```

```powershell
.venv311/Scripts/python.exe -m unittest docs.check_leap_calibration docs.check_lane_transition docs.check_leap_input -v
```

EXTRACTED: 소스 검사 12개 통과. 보정 계산·부족 측정·동작 분리 부족, 개인별 저장·선택·기본값 전환, 잘못된 값과 파일 손상 시 원본 유지, 트래커의 선택 임계값 적용, 보정 창의 중복 프레임 제외·저장·종료를 검사했다. 기존 4레인·카메라 제외·노트 제약 검사도 통과했다.

EXTRACTED: 새 EXE 자체 검사 10항목 통과(`ok=true`). 보정 임계값 계산·임시 프로필 저장/기본값 전환·보정 창 렌더링, SDK 로딩 및 실제 무곡 게임의 레인 제약을 확인했다. 보고서는 `release/self-test-leap-personal-calibration-2026.11.18.json`과 실행 폴더의 `self-test.json`에 저장했다. 자체 검사는 임시 프로필만 쓰며 실제 개인별 보정 파일을 변경하지 않는다.

AMBIGUOUS: 실사용자의 손으로 단계별 보정과 보정 후 핀치 정확도를 확인해야 한다. 위 거리 기준은 참고 실험의 휴리스틱이며 정확도를 보장하는 측정 결과는 아니다. 보정 대상은 현재 오른손이다.

[Mermaid 보정 흐름](../diagrams/leap-personal-calibration.md)은 Mermaid 지원 Markdown 미리보기에서 연다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 보고서는 자동 갱신하지 않았다.
EXTRACTED: 최신 버전은 설정 버튼 대신 매 게임 시작 전 새 측정을 요구합니다. [현재 보정 절차](pre-game-calibration.md)를 먼저 확인하세요. 아래 설정·기존값 적용 절차는 이전 버전 기록입니다.
