# Armband 연결 유지와 음악 경로 검증

EXTRACTED: 2026-11-18 작업 트리 기준 기록이다. 배포된 EXE의 검증 결과와 구분한다. 이번 이어서 작업에서는 사용자가 제공한 AGENTS.md의 문서화 전용 범위를 적용하여 게임 소스를 추가 수정하거나 새 EXE를 만들지 않았다.

## 소스에서 확인한 동작

EXTRACTED: `app/input/emg_session.py`의 EMGSession은 화면마다 reader를 새로 만드는 대신 EMGLease를 제공한다. lease 종료는 공유 reader를 닫지 않는다. 정상 연결된 OYMotion 장치의 Auto/실제 COM 및 저장된 장치 정보가 일치하면 연결을 재사용한다. OYMotion에 적용되지 않는 기존 baud/signal 옵션 변경도 이 재사용 조건에서 제외한다.

EXTRACTED: `app/ui/main_window.py`의 핀치 진입 경로는 공유 EMG 세션을 종료하지 않는다. 핀치 보정과 게임의 입력은 Leap 전용으로 유지한다. 앱 종료의 shutdown 또는 장치 변경·오류 후 acquire는 실제 reader를 닫거나 교체할 수 있다.

EXTRACTED: `app/ui/start_screen.py`의 곡 선택은 미리보기뿐 아니라 실제 selected_song_path를 갱신한다. `MainWindow._ensure_song_notes`는 선택 곡의 유효 채보가 없으면 분석·생성을 요청하고 완료 후 화면 전환을 재개한다. 곡이 변경되면 해당 곡으로 생성한다.

EXTRACTED: `app/audio/note_generator_adapter.py`의 저장 채보는 schema_version 3이며 파일 이름·크기·mtime_ns로 원본을 식별한다. 메타데이터가 없는 이전 채보는 재사용하지 않는다. 실곡 분석 또는 생성 실패는 오류로 전달하며 실곡에 샘플 노트를 대신 넣지 않는다. 곡을 선택하지 않은 샘플 모드는 별도 경로다.

EXTRACTED: `app/audio/audio_player.py`는 오디오 출력 지연을 재생 시계에 반영한다. `app/ui/game_widget.py`는 선택 곡의 재생 오류 시 게임을 중단하고 오류를 알린다. 오류 이후 벽시계로 무음 노트를 진행하지 않는다.

INFERRED: 곡 선택 상태와 채보 캐시의 연결을 확인하면 다른 곡 또는 샘플 채보로 시작할 가능성을 줄일 수 있다. 이것만으로 사용자가 느끼는 박자 일치 정확도를 증명하지는 않는다.

## 이번 검증

EXTRACTED: 기존 검사 15개 모듈, 총 75개 테스트가 통과했다. `docs/check_song_playback.py`에는 실제 곡 분석 실패 시 샘플 대체 금지, 캐시 식별, 클릭한 곡 선택과 생성, 정상 USB 세션 재사용, 재생 오류 시 중단 검사가 포함된다. 장치 연결 관련 검사는 모의 reader를 사용한다.

EXTRACTED: `WorkOrder/verify_full_song.py`는 오디오 디코딩·취소 검사 뒤 `GameWidget._should_finish` 검사에서 실패했다. 테스트의 SimpleNamespace에 현재 코드가 요구하는 `mode`가 없어 AttributeError가 발생했다. 전체 곡 완료 검사 통과로 기록하지 않는다. 해당 파일은 이번에 수정하지 않았다.

EXTRACTED: 기존 배포 폴더에 저장된 BIGBANG MP3를 실제 분석하여 BPM 126.048, 분석 길이 208.013초, 핀치 노트 208개를 얻었다. 첫 노트는 221ms, 마지막 노트는 202861ms다. 이전 디코딩 확인의 원본 길이는 213.773초였다. 이번 분석은 메모리에서만 수행했으며 사용자 곡이나 채보 파일을 덮어쓰지 않았다.

EXTRACTED: 같은 파일의 soundfile 정보는 44100Hz, 9427392프레임, 213.773초다. 읽어 본 `legacy_web/backend/audio_analyzer.py`에는 명시적인 무음 제거 호출이 없다.

AMBIGUOUS: 동일 파일의 분석 길이와 soundfile 길이가 다른 원인은 확정하지 않았다. 분석 실행 경로와 디코더가 원본 재생 시점과 어긋나는지 추가 확인이 필요하다. 노트 개수나 분석 성공만으로 음악 동기화가 해결됐다고 판단할 수 없다.

AMBIGUOUS: 실제 착용 상태에서 장시간 연결 유지, 전체 곡 스피커 출력과 청감상 노트 동기화는 이번 검사로 확인되지 않았다. USB 분리·전원 손실 등 물리적 연결 단절까지 막는다는 의미가 아니다. 새 EXE 및 배포 자체 검증도 남아 있다.

## 보기와 남은 작업

[연결·음악 흐름도](../diagrams/music-session-review.md)를 Mermaid 지원 Markdown 미리보기로 연다. Graphify는 저장소 루트에서 `graphify .`로 수동 실행한다. 필요한 경우 먼저 `pip install graphifyy`를 실행한다. 기존 출력 갱신 명령은 `graphify update .`이며 이번에는 실행하지 않았다.

TODO: 코드 변경을 허용하는 작업 범위에서 전체 곡 검사 fixture의 mode를 갱신하고 재실행한다. 실제 USB/armband 및 오디오 출력으로 검증한 다음 새 EXE를 빌드·검증한다.
