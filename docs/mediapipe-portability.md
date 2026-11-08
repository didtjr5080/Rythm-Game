# 다른 PC 및 한글 경로의 MediaPipe

## 확인한 문제와 수정

EXTRACTED: 동일한 MediaPipe 0.10.21 모델을 영문 경로에서는 실행할 수 있었지만, 한글 경로에서는 `hand_landmark_tracking_cpu.binarypb`를 찾지 못하는 오류를 재현했습니다. Python에서 해당 파일이 존재하는데도 네이티브 모델 로더가 실패했습니다.

INFERRED: 사용자가 보고한 다른 PC의 증상도 이 경로 문제일 가능성이 있으나, 해당 PC의 오류 로그로 확정한 것은 아닙니다. 관련 원본 보고는 [MediaPipe 공식 저장소의 Unicode 경로 이슈](https://github.com/google-ai-edge/mediapipe/issues/2677)를 참고합니다.

EXTRACTED: `app/input/mediapipe_runtime.py`가 Windows에서 영문 짧은 경로를 우선 사용하고, 사용할 수 없으면 필요한 모델만 영문 경로의 캐시에 복사합니다. 버전별 모델 내용 해시로 캐시를 구분하고 손상된 파일은 복구합니다. 카메라 영상·EMG 값은 이 캐시에 저장하지 않습니다.

EXTRACTED: 임시 경로가 한글인 경우에는 영문 경로의 공용 문서 폴더를 대안으로 사용합니다. 쓰기 가능한 영문 경로를 확보하지 못하면 전체 ZIP을 영문 경로에 압축 해제하라는 오류를 표시합니다.

EXTRACTED: `EMG-Motion-Rhythm.spec`은 MediaPipe에 필요한 C++ 런타임을 EXE 인접 내부 폴더에도 포함하고 Qt 폴더의 사본과 버전을 맞춥니다. MediaPipe를 Qt보다 먼저 로드하는 기존 순서를 유지합니다. EXE 자체 검사는 C++ 런타임이 시스템 설치가 아닌 배포 폴더에서 로드됐는지도 확인합니다. 배포 방식은 [Microsoft의 application-local 배포 안내](https://learn.microsoft.com/en-us/cpp/windows/deployment-in-visual-cpp?view=msvc-170)를 참고합니다.

## 상태 확인

1. **설정 → Connect / Test Camera**를 실행합니다.
2. `MEDIAPIPE READY / tracking`은 관절 추적 중, `MEDIAPIPE READY / no hand`는 모델은 동작하지만 손을 찾지 못한 상태입니다.
3. `MEDIAPIPE INACTIVE`이면 초기화 또는 처리 오류를 함께 표시합니다. `APPROXIMATE OPENCV FALLBACK`은 정밀 MediaPipe 추적이 아니라 대체 인식이라는 뜻입니다.

EXTRACTED: 초기화 오류는 OpenCV 대체 인식이 실행돼도 지워지지 않습니다. 로비·캘리브레이션·게임에서도 MediaPipe가 활성화되지 않았다는 안내를 표시합니다.

## 검증

```powershell
.venv311/Scripts/python.exe WorkOrder/verify_mediapipe_portability.py
EMG-Motion-Rhythm.exe --self-test self-test.json
```

EXTRACTED: 소스 검증은 한글 모델 경로, 영문 짧은 이름을 사용할 수 없는 상황, 손상된 캐시 복구, 초기화 실패 후 오류 유지, 임시 경로가 한글인 상황의 대안 선택을 검사합니다. 임시 경로 전환 후 Python 모듈 메타데이터도 복원합니다.

EXTRACTED: 자체 검사 결과에는 `unicode_model_inference`, `model_path_ascii`, `cpp_runtime`를 기록합니다. 빈 영상 추론의 성공은 모델 실행 확인이며 실제 사용자의 카메라·손 인식 정확도 측정은 아닙니다.

AMBIGUOUS: 다른 PC의 카메라 해상도·조명·드라이버와 실제 손 자세에 따른 인식 정확도는 그 PC에서 추가 확인해야 합니다.
