# MyStoryPal: Interactive English Storybook

## 응용 프로그램 설명

**MyStoryPal**은 **Edge AI 기반 아동 영어 동화 창작 애플리케이션**입니다. 아동이 AI와 실시간으로 대화하며 영어 동화를 함께 만들어가는 과정에서 자연스럽고 재미있는 방식으로 영어 학습을 할 수 있도록 설계되었습니다.
클라우드 기반 AI 서비스와 달리 본 앱은 모든 AI 연산을 기기 내 NPU에서 수행하며 Edge AI의 강점을 최대한 활용합니다.

**MyStoryPal의 특징**
1. 채팅형 동화 공동 창작: 아동이 문장이나 아이디어를 입력하면 AI가 이에 맞는 동화 문장을 이어서 생성합니다. 이 과정을 반복하며 점차 하나의 이야기를 완성해 나갈 수 있습니다.
2. 영어 문법 및 어휘 피드백: 아동이 입력한 영어 문장에 문법 오류나 오타가 있으면 교정해 주며, 단어의 뜻을 물어보면 친절하게 설명해 줍니다. 피드백 구조를 통해 자연스럽게 영어 실력을 키울 수 있습니다.
3. 삽화가 담긴 나만의 동화책 제작: 이야기 문장이 4개씩 쌓일 때마다 그 내용에 어울리는 동화풍 이미지를 생성합니다. 이로써 더욱 몰입감있게 동화책을 만들어나갈 수 있습니다.

**Edge AI 기반 구조의 장점**
- 초저지연 반응성: 모든 텍스트 및 이미지 생성이 디바이스(Copilot+ PC) 내에서 실행되어 반응 속도가 빠릅니다.
- 완전한 오프라인 작동: 네트워크 연결 없이 동작하므로 오프라인 환경에서도 교육을 지속할 수 있습니다.
- 데이터 프라이버시 보장: 아동의 입력한 텍스트, 대화 내용, 생성된 이미지를 외부 서버로 전송하지 않아 민감 정보를 보호합니다.

---

## 응용 프로그램 사용 방법
1. 사용자가 채팅 인터페이스에 영어로 이야기 시작 문장을 입력합니다.
   - 예: `There was prince` (문법 오류가 있는 문장 예시)
2. AI는 사용자 입력에서 문법을 오류를 교정한 뒤, 자연스러운 이야기를 이어갑니다. 또한 이야기 내용으로 삽화 이미지를 생성해 보여줍니다.
   - 텍스트 생성: Phi-3-mini-128k-instruct 모델
   - 이미지 생성: Stable-Diffusion-v1.5 모델
3. 사용자는 AI가 생성한 이야기 내용과 삽화를 확인하고, 다음 문장을 입력해 이야기를 이어갑니다.
4. 이야기를 완성하고 스토리북으로 저장할 수 있습니다.
<img width="1512" height="945" alt="스크린샷 2025-07-28 오전 1 20 08" src="https://github.com/user-attachments/assets/3e913448-6c8f-4e87-ada2-45584f557534" />
<img width="1512" height="944" alt="스크린샷 2025-07-28 오전 1 31 54" src="https://github.com/user-attachments/assets/ce3fdcfe-8431-42cd-8d21-9c8238514f46" />

---

## 팀 구성원
| 이름 | 이메일 | 퀄컴 ID |
|:---  |---  |---  |
| 도규엽 | bestornot04@naver.com | bestornot04@naver.com |
| 도연수 |shnystar1129@ewhain.net | shnystar1129@ewhain.net |
| 백승우 | tmddn7675@gmail.com | tmddn7675@gmail.com |
| 이서현 | leeseohyun@ewhain.net | leeseohyun@ewhain.net |
| 최윤진 | cyy000123@gmail.com | cyy000123@gmail.com |


## 응용 프로그램 설치 및 실행 방법
가상환경에서(venv 등) 아래의 의존성들을 설치해야 합니다.

### 사용 패키지
```
=== Runtime versions ===
Python            : 3.12.11
torch             : 2.6.0+cu118
torch cuda        : 11.8
transformers      : 4.54.0
accelerate        : 1.9.0
PySide6 binding   : 6.9.1
Qt runtime        : 6.9.1
diffusers
```

### 터미널에서 실행하는 방법
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
---

## 오픈소스 라이선스

본 프로젝트는 MIT 라이선스 하에 배포됩니다.
또한, 본 프로젝트는 다음과 같은 세 번째 파티 오픈소스 구성요소 및 모델을 사용하고 있습니다.
각 패키지 및 모델의 라이센스 상세 조건은 LICENSE 파일 또는 Hugging Face 모델 카드(Model Card)에서 확인하실 수 있습니다.

#### 런타임 및 라이브러리
- Python runtime: Python 3.12.11
- torch v2.6.0+cu118: BSD‑3‑Clause License
- torchaudio v2.6.0: BSD‑3‑Clause (PyTorch와 동일 라이선스)
- torchvision v2.6.0: BSD‑3‑Clause
- transformers v4.54.0: Apache License 2.0 (코드 레벨)  
- accelerate v1.9.0: Apache License 2.0 (특허권 포함)
- diffusers: Apache License
- PySide6 v6.9.1: LGPL‑3.0‑only 또는 GPL‑3.0‑only 
  ※ 상업적 배포 시 LGPL 조건 준수가 필요합니다.

#### 사전학습 모델
- Phi‑3‑mini‑128k‑instruct: MIT License
- Stable Diffusion v1.5: CreativeML OpenRAIL‑M License
