import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 170)  # Скорость речи
engine.setProperty('volume', 1.0)  # Громкость

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[Озвучка]: ошибка — {e}")