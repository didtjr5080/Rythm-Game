# 음악 원본·시간축·전체 곡 종료

EXTRACTED: 이 문서는 2026.11.18.2 음악 구현 기록이다. 후속 2026.11.18.4의 종료 조건과 근전도 채보는 [연속 MISS10·긴 노트 전용 규칙](game-rule-update.md)을 우선한다.

EXTRACTED: 2026-11-18, GitHub `11c99ac7952b1ed719ffa4cd584371b9935ddbf4`를 기준으로 음악 과제를 구현했다. 사용자 지시에 따라 음악 adapter·재생 수명·곡 종료 처리와 검증을 수정했다. 기존 게임 선택 UI, Leap 핀치·OYMotion 암밴드 입력과 `legacy_web` 소스는 보존했다.

## 구현

EXTRACTED: 분석 시작과 종료, 채보 저장 시점의 원본 정보를 비교한다. 파일명·크기·mtime_ns에 SHA256을 추가해 같은 크기와 수정 시각으로 교체된 곡도 구분한다. 분석 중 또는 분석 후 원본 변경은 오류로 전달하고 기존 채보를 덮어쓰지 않는다. 분석 결과와 채보에는 실제 분석 모듈 경로, 샘플레이트, PCM 기준 프레임 수와 시간 기준도 기록한다.

EXTRACTED: 재사용 채보는 두 모드 모두 파싱할 수 있어야 한다. 빈 근전도 채보, 잘못된 시간 값, 음수 노트 시각은 재생성 대상으로 처리한다. 이전 SHA256 없는 채보도 재생성한다. 기존 자동 생성 흐름은 유지하므로 필요하면 게임 선택 진입에서 다시 생성한다. 곡이 없는 명시적 샘플 모드는 유지하고, 유효하지 않은 실곡 분석은 샘플로 대체하지 않는다.

EXTRACTED: 재생 데이터가 비었거나 NaN/Inf를 포함하면 출력 전에 오류 처리한다. 출력 지연을 반영하는 기존 시계는 유지한다. 취소하면 재생 위치를 고정하고 재시작하면 길이·지연·위치를 초기화한다. 정상 출력 완료 위치는 실제 PCM 끝으로 고정한다. 취소한 화면에 남은 타이머 호출은 판정을 실행하지 않는다.

EXTRACTED: 정상 곡 종료 시 아직 처리되지 않은 노트를 MISS로 한 번만 집계한다. 기존 근전도 마지막 유지 노트의 종료 유예와 핀치 연속 MISS 10회 종료는 유지한다. 재생 오류나 사용자 취소는 이 정상 종료 집계를 실행하지 않는다.

## 실제 MP3 시간축

EXTRACTED: `app/data/songs/BIGBANG*.mp3` SHA256은 `19ffd9d81fe083b1d079e810e3bb595c110265b8c99314d66ba6c99f55f2c662`다. Python 3.11, librosa 0.11.0, soundfile 0.14.0, libsndfile 1.2.2에서 재검증했다. 분석 모듈은 저장소 `legacy_web/backend/audio_analyzer.py`, 분석 loader는 현재 가상환경의 librosa이고 재생 decoder는 soundfile이다.

| 측정 | 프레임 수 | 샘플레이트 | 길이 |
| --- | ---: | ---: | ---: |
| soundfile.info 메타데이터 | 9,427,392 | 44,100Hz | 213.773061초 |
| 실제 분석·재생 PCM | 9,173,376 | 44,100Hz | 208.013061초 |

EXTRACTED: 재생 PCM을 채널 평균한 전체 파형과 분석 모노 파형의 최대 절대 오차는 0.0이다. 이 환경에서 차이는 메타데이터와 실제 디코딩 결과 사이에 있으며 분석·재생 PCM 사이에는 없다. 5.76초 차이를 보정하기 위해 노트 시간을 늘리지 않았다. 파일 헤더의 구체적 원인은 별도 디코더 비교 없이 단정하지 않는다.

EXTRACTED: 실제 곡에서 생성한 채보의 시작·중간·끝 노트 시각에 엔진 기준선 좌표가 정확히 일치하는지 두 모드에서 확인했다. 핀치 시각은 221/102063/202861ms, 근전도 시각은 2159/103515/201421ms다. 이는 엔진 좌표 계산 검사이며 실제 GUI 프레임·스피커 동시 측정은 아니다.

## 검증과 재실행

EXTRACTED: 이번 구현은 `dist_windows_music_20261118_2/EMG-Motion-Rhythm/EMG-Motion-Rhythm.exe`에 빌드했다. 소스·EXE 자체 검사 각각 19개 항목이 통과했다. EXE 검사에서는 개발 SDK 환경 변수를 해제하고 번들 SDK를 확인했다. [배포 안내](windows-release.md)에 파일 경로와 검증 범위를 기록한다.

EXTRACTED: 기존 75개와 추가 14개를 합친 89개 검사가 통과했다. 추가 검사는 원본 교체·분석 중 변경·저장 전 변경, 유효하지 않은 분석·캐시, 전체 PCM 제출, 지연 반영 시계, 취소·재시작·오류, 양 모드 214초 시뮬레이션과 마지막 유지 노트, 자연 종료 누락 방지를 포함한다. 전체 곡 스크립트는 현재 mode/rest_baseline 객체 구조를 반영했으며 과거 AttributeError를 해결했다.

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
.venv311/Scripts/python.exe -m unittest discover -s docs -p 'check_*.py'
.venv311/Scripts/python.exe WorkOrder/verify_full_song.py --real-song --report release/music-implementation-check.json
```

EXTRACTED: 다른 원본은 `--song '곡 경로'`로 지정한다. 실제 파일 전체 디코딩·분석·파형 비교와 전체 PCM의 출력 함수 전달은 수행하지만, 출력 장치는 모의 객체다. `--real-song`은 로컬 BIGBANG 파일이 있어야 한다. 사용자의 원본 곡·저장 설정·개인 프로필·기존 채보를 검증 중 덮어쓰지 않는다.

AMBIGUOUS: 스피커 출력 지연의 정확도, 실제 GUI 프레임 오차와 긴 재생의 장치 시계 드리프트는 실기 측정이 필요하다. 센서 30분 유지와 물리적 분리·복구도 이 음악 자동 검사로 보장하지 않는다.

EXTRACTED: [음악 시간축 도식](../diagrams/music-timeline.md)은 Mermaid 지원 Markdown 미리보기로 확인한다. Graphify는 저장소 루트에서 `graphify .`, 기존 출력 갱신은 `graphify update .`로 수동 실행한다. 이번에는 실행하지 않았다.
