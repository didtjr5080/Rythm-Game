# 근전도 3.0초 기록·최저값 기준 신전

EXTRACTED: 2026.11.18.7부터 [사람별 프로필](player-profiles.md)에 저장된 기준이 있으면 재측정 없이 사용한다. 값이 없거나 사용자가 재측정을 위해 지운 경우에만 아래3.0초 기록을 수행한다. 프로필 없는 연습은 매번 측정한다.

EXTRACTED: 2026.11.18.6의 [핀치+신전 상위 모드](pinch-extension-mode.md)도 같은3.0초 최저값 기준을 사용한다. 기본 핀치 모드에는 근전도 측정을 추가하지 않았다.

EXTRACTED: 2026-11-18 사용자 요청으로 근전도 게임의 시작 전 기준을 평균+0.01에서 **3.0초 측정 구간의 최저값**으로 변경했다. 매 게임 새로 기록하며 음악과 노트는 기록을 마친 뒤 시작한다. 현재 유효한 값이 **최저값 이상(같은 값 포함)**이면 신전으로 판정한다. 추가 여유값·잡음 차이·기존 ON/OFF는 적용하지 않는다.

EXTRACTED: 비교에는 반올림 전 측정값을 사용한다. 예를 들어 측정 최저값184.991이면 184.991은 신전, 184.9909는 기준 미만이다. 실제 최저값이0이면 유효한0도 신전이다. 화면 값은 소수4자리로 표시하며 표시는 판정값을 변경하지 않는다.

EXTRACTED: 타이머는 첫 유효 표본에서 시작하고3.0초 미만에서는 기준을 확정하지 않는다. 3.0초 이후 도착한 UI 호출의 새 표본 묶음은 기록에 넣지 않는다. SDK 표본에 개별 시각이 없으므로 소프트웨어 호출 시각 기준으로 구간을 구분하며, 하드웨어 표본 단위의 정확한3초 길이를 검증한 것은 아니다. 측정 도중 수신이 끊기면 해당 구간을 버리고 새로 연속3초를 측정한다. 표본이 전혀 없으면 가짜0기준을 만들지 않고 대기한다. 끊긴 신호는 신전으로 판정하지 않는다.

EXTRACTED: 측정 목록은 `RestBaseline.samples`에 남기고, 정상 결과 기록에는 `emg_baseline_samples`, `emg_rest_baseline`, `emg_baseline_method=minimum`, `emg_baseline_duration_seconds=3.0`, `emg_activation_delta=0.0`을 기록한다. 재생 전 취소한 게임은 기존 취소 흐름을 따른다. 기준은 과거 설정에 고정 저장하지 않고 매 게임 새로 측정한다.

EXTRACTED: `app/input/rest_baseline.py`, 게임 내 비교·HUD·결과 메타데이터와 자체 검사를 수정했다. Leap·armband SDK 수신 경로, 근전도 긴 노트 전용, 양 모드 연속MISS10종료는 유지했다. 전체95개 검사 통과. 최소값·같음/미만 경계·반올림 전 비교·3초 완료·지연 호출·빈 표본·신호 손실·새 게임 재측정·게임 득점·결과 기록을 검증했다.

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
.venv311/Scripts/python.exe -m unittest discover -s docs -p 'check_*.py'
```

EXTRACTED: [측정·판정 도식](../diagrams/emg-rest-baseline.md)은 Mermaid 지원 Markdown 미리보기로 연다. Graphify는 저장소 루트에서 `graphify .` 또는 `graphify update .`로 수동 실행한다. 이번에는 실행하지 않았다.

AMBIGUOUS: 실제 착용 상태의 구간 기록과 신전 표시는 실기 확인이 필요하다.

EXTRACTED: `dist_windows_minimum_20261118_5/EMG-Motion-Rhythm/EMG-Motion-Rhythm.exe`로 빌드했고 최종EXE 자체검사19항목 통과(`emg_baseline_method=minimum`, `emg_activation_delta=0.0`). ZIP 무결성·전체파일일치·개인데이터제외를 확인하고 이전 실행 폴더의 사용자 데이터54파일을 해시 검증해 보존했다. [배포 안내](windows-release.md)에 파일·검증 보고서를 기록했다.
