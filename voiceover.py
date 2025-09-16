import pyttsx3

voiceoverDir = "Voiceovers"

def create_voice_over(filePath, text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    engine.setProperty('rate', 125)
    engine.setProperty('volume', 0.8)

    engine.say("This is a test using a different voice.")
    engine.save_to_file(text, filePath)
    engine.runAndWait()
    return filePath

def test():
    filepath = "test.mp3"
    text = "This is a test"
    create_voice_over(filepath, text)
    print("Voiceover created at: ", filepath)

if __name__ == "__main__":
    test()
