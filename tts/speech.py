import pyttsx3

def speech(text: str):
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)  # 말하기 속도 조정
    engine.say(text)                 # 전달받은 문자열 읽기
    engine.runAndWait()              # 실행
