import pyttsx3

def speech():
    engine = pyttsx3.init()
    engine.setProperty("rate", 160) # 슬라이드바에 TTS 속도 조절을 가능하게 하면 더 유용하게 UI를 구성할 수 있을 듯
    engine.say("안녕하세요. 저는 한국어 화자입니다.")
    print("Rate:", engine.getProperty('rate'))
    print("Volume:", engine.getProperty('volume'))
    print("Current voice:", engine.getProperty('voice'))

    print("\nAvailable voices:")
    for v in engine.getProperty('voices'):
        print("-", v.id, v.name, v.languages)

    for voice in engine.getProperty('voices'):
        if "en-US" in voice.id:   # 미국 음성
            print("Selected (US):", voice.id)
            engine.setProperty('voice', voice.id)
            engine.say("Hello, I am speaking in an American English voice.")
    engine.runAndWait()   # 큐에 쌓인 발화 순차 실행

speech()
