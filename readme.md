## MyStoryPal: Interactive English Storybook

### Dependencies
실행을 위해 가상환경에서(venv 등) 아래의 의존성들을 설치해야 합니다.

=== Runtime versions ===
Python            : 3.12.11
torch             : 2.6.0+cu118
torch cuda        : 11.8
transformers      : 4.54.0
accelerate        : 1.9.0
PySide6 binding   : 6.9.1
Qt runtime        : 6.9.1
diffusers

### 응용프로그램 실행 방법
1. venv 등의 가상환경에 pip로 의존성 패키지들을 설치합니다.
2. python main.py를 입력해 애플리케이션을 실행합니다. (모델 설치에 시간 소요)
3. 애플리케이션 GUI에 질문을 입력하고, LLM(Phi-3-mini-128k-instruct) 응답과 Stable Diffusion 모델로 생성된 이미지를 확인합니다.
