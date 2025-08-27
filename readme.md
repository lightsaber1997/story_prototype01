# MyStoryPal: Interactive English Storybook

## Application Description

**MyStoryPal** is an **Edge AI-based children's English storybook creation application**. It is designed to enable children to learn English naturally and enjoyably through real-time conversations with AI while collaboratively creating English stories.

Unlike cloud-based AI services, this app performs all AI computations on the device's NPU, maximizing the advantages of Edge AI.

**Features of MyStoryPal:**

1. **Conversational Story Co-creation**: When children input sentences or ideas, the AI generates appropriate story sentences in continuation. Through this repetitive process, they can gradually complete a story together.

2. **English Grammar and Vocabulary Feedback**: If there are grammatical errors or typos in the English sentences entered by children, the app corrects them. When children ask about word meanings, it provides friendly explanations. Through this feedback structure, children can naturally improve their English skills.

3. **Creating Personalized Illustrated Storybooks**: Every time four story sentences accumulate, the app generates fairy tale-style images that match the content. This creates a more immersive storybook creation experience.

**Advantages of Edge AI-based Architecture:**

- **Ultra-low Latency Response**: All text and image generation is executed within the device (Copilot+ PC), resulting in fast response times.
- **Complete Offline Operation**: Works without network connection, allowing continuous education even in offline environments.
- **Data Privacy Protection**: Does not transmit children's input text, conversation content, or generated images to external servers, protecting sensitive information.

---

## How to Use the Application
> server repository - https://github.com/lightsaber1997/chat_server_share
1. Follow the instructions in the Readme.md of the server repository to run the C++-based local server on port 8080. 
2. Download and place the CLIP, Stable Diffusion v2.1, and piper-voices models under the data/ directory. 
3. Set up a virtual environment, install the required packages listed in requirements.txt, and run main.py. 
4. Launch the app. Once you attach an image and start, the user begins the story. 
5. The AI corrects grammatical errors in the user’s input and continues the story naturally. It also generates and displays illustrations based on the story. 
  - Text Generation: Llama-v3.2-3B-Instruct (running on the server)
  - Image Generation: Stable Diffusion v2.1
  - Image-to-Text: CLIP
6Users can review the AI-generated story content and illustrations, then input the next sentence to continue.
7. The completed storybook can be exported as a PDF.

<img width="965" height="554" src="https://github.com/user-attachments/assets/6a584e59-9fd9-4896-a27c-7efb98400348" />
<img width="969" height="557" src="https://github.com/user-attachments/assets/b8f8fa5a-625b-4576-8e65-2230223ff9a7" />

---

## Team Members

| Name | Email | Qualcomm ID |
|:--- |--- |--- |
| Do Gyuyeop | bestornot04@naver.com | bestornot04@naver.com |
| Do Yeonsu | shnystar1129@ewhain.net | shnystar1129@ewhain.net |
| Baek Seungu | tmddn7675@gmail.com | tmddn7675@gmail.com |
| Lee Seohyun | leeseohyun@ewhain.net | leeseohyun@ewhain.net |
| Choi Yoonjin | cyy000123@gmail.com | cyy000123@gmail.com |

## Installation and Execution Instructions

The following dependencies must be installed in a virtual environment (venv, etc.).

### Required Packages

```
=== Runtime versions ===
onnxruntime-qnn==1.22.0
qai_hub_models[stable-diffusion-v2-1-quantized]==0.29
piper-tts==1.3.0
# pip uninstall onnx-runtime 필요
# torch==2.4.1

# Core numerical + image stack
numpy>=1.23
Pillow>=9.0

# Hugging Face ecosystem
transformers>=4.30
diffusers>=0.20
accelerate>=0.20  # usually needed with diffusers

# open AI (for debugging)
openai

# PySide GUI
PySide6==6.9.1

# API, env management
python-dotenv

# tts
pyttsx3==2.99

```

### Terminal Execution Method

1. Create and activate virtual environment
    (1) Create virtual environment
    ```bash
    python -m venv .venv
    ```
    (2) Activate virtual environment
    ```bash
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

2. Install required packages
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt # or individual installation
    ```

3. Run main.py
    ```bash
    python main.py
    ```

---

## Open Source License

This project is distributed under the MIT License.

Additionally, this project uses the following third-party open source components and models.

Detailed license conditions for each package and model can be found in the LICENSE file or Hugging Face Model Cards.

#### Runtime and Libraries
| Package                                                | Version/Range   | License                        |
|--------------------------------------------------------|-----------------|--------------------------------|
| onnxruntime-qnn                                        | 1.22.0          | MIT                            |
| qai_hub_models[stable-diffusion-v2-1-quantized]        | 0.29            | Apache License 2.0             |
| piper-tts                                              | 1.3.0           | MIT                            |
| torch                                                  | 2.4.1           | BSD-3-Clause                   |
| numpy                                                  | >=1.23          | BSD-3-Clause                   |
| Pillow                                                 | >=9.0           | HPND (similar to BSD)          |
| transformers                                           | >=4.30          | Apache License 2.0             |
| diffusers                                              | >=0.20          | Apache License 2.0             |
| accelerate                                             | >=0.20          | Apache License 2.0             |
| openai                                                 | latest          | Apache License 2.0             |
| PySide6                                                | 6.9.1           | LGPL v3 (with Qt exceptions)   |
| python-dotenv                                          | latest          | BSD-3-Clause                   |
| pyttsx3                                                | 2.99            | BSD                            |

#### Pre-trained Models
| Component        | Model / Library                   | License            |
|------------------|-----------------------------------|--------------------|
| Text Generation  | Llama-v3.2-3B-Instruct            | Meta Llama 3.2 Community License (non-commercial unless commercial license obtained) |
| Image Generation | Stable Diffusion v2.1             | CreativeML Open RAIL-M (Responsible AI License) |
| Image-to-Text    | CLIP                              | MIT                |

