## MyStoryPal: Interactive English Storybook

### 응용 프로그램에 대한 설명

**MyStoryPal**은 **Edge AI 기반 아동 영어 동화 창작 애플리케이션**입니다. 아동이 AI와 실시간으로 대화하며 영어 동화를 함께 만들어가는 과정에서 자연스럽고 재미있는 방식으로 영어 학습을 할 수 있도록 설계되었습니다.
클라우드 기반 AI 서비스와 달리 본 앱은 모든 AI 연산을 기기 내 NPU에서 수행하며 Edge AI의 강점을 최대한 활용합니다.

**MyStoryPal의 특징**
- 실시간 인터랙티브 스토리 생성: 아동이 먼저 이야기를 시작하면, AI가 스토리를 이어가며 삽화 이미지를 생성해 이야기 진행 몰입도를 높입니다.
- 영어 문장 피드백 제공: 아동이 입력한 영어 문장에서 문법 오류나 어색한 표현이 있을 경우 피드백해 문장력을 향상에 도움을 줍니다.
- 스토리북 저장: 생성된 스토리를 이미지와 함께 저장하면 반복 학습이 가능합니다.

**Edge AI 기반 구조의 장점**
- 초저지연 반응성: 모든 텍스트 및 이미지 생성이 디바이스(Copilot+ PC) 내에서 실행되어 반응 속도가 빠릅니다.
- 완전한 오프라인 작동: 네트워크 연결 없이 동작하므로 오프라인 환경에서도 교육을 지속할 수 있습니다.
- 데이터 프라이버시 보장: 아동의 입력한 텍스트, 대화 내용, 생성된 이미지를 외부 서버에 전송하지 않아 민감 정보를 보호합니다.

### 응용 프로그램 실행 방법
1. 애플리케이션 좌측의 GUI에 질문을 입력합니다.
   `ex. There was a prince`
2. Phi-3-mini-128k-instruct 모델로 생성된 텍스트와 Stable-Diffusion-v1.5 모델로 생성된 이미지를 확인합니다.

---

### 팀 구성원
| 이름 | 이메일 | 퀄컴 이메일 |
|:---  |---  |---  |
| 도규엽 | bestornot04@naver.com | bestornot04@naver.com |
| 도규엽 |shnystar1129@ewhain.net | shnystar1129@ewhain.net |
| 백승우 | tmddn7675@gmail.com | tmddn7675@gmail.com |
| 이서현 | leeseohyun@ewhain.net | leeseohyun@ewhain.net |
| 최윤진 | cyy000123@gmail.com | cyy000123@gmail.com |


### 응용 프로그램 설치 방법
가상환경에서(venv 등) 아래의 의존성들을 설치해야 합니다.

#### 사용 패키지
=== Runtime versions ===
Python            : 3.12.11
torch             : 2.6.0+cu118
torch cuda        : 11.8
transformers      : 4.54.0
accelerate        : 1.9.0
PySide6 binding   : 6.9.1
Qt runtime        : 6.9.1
diffusers

### 응용 프로그램 실행 방법
1. 가상환경 생성 및 활성화

    (1) 가상환경 생성
    ```bash
    python -m venv .venv
    ```
    (2) 가상환경 활성화
    ```bash
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```
2. 필요 패키지 설치
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt # 또는 개별 설치
    ```
3. main.py 실행
    ```
    python main.py
    ```
    > ⚠️ 최초 실행 시 모델이 다운로드되며 수 분 정도 소요될 수 있습니다.