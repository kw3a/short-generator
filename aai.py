from moviepy.editor import os
import assemblyai as aai

def assemblyLanguageCode(language):
    languages = {
        'spanish': 'es',
        'english': 'en'
    }
    return languages[language]

def transcribe_audio(aai_key, audio_file, language_code) -> list[aai.Word] | None:
    aai.settings.api_key = aai_key
    config = aai.TranscriptionConfig(language_code=language_code)
    transcriber: aai.Transcriber = aai.Transcriber(config=config)
    transcript: aai.Transcript = transcriber.transcribe(audio_file)
    return transcript.words

if __name__ == "__main__":
    api_key = ""
    target_path = os.path.join("to_upload", "spanish", "2024-09-01", "0", "output.mp3")
    language_code = "es"
    words = transcribe_audio(api_key, target_path, language_code)
    if words == None:
        print("Error transcribing audio.")
        exit()
    for word in words:
        print(f"Texto: {word.text}")
        print(f"Inicio: {word.start} ms")
        print(f"Fin: {word.end} ms")
        print(f"Confianza: {word.confidence}")
        print(f"Hablante: {word.speaker}")
        print("-" * 40)
"""
for word in transcript.words:
    print(f"Texto: {word.text}")
    print(f"Inicio: {word.start} ms")
    print(f"Fin: {word.end} ms")
    print(f"Confianza: {word.confidence}")
    print(f"Hablante: {word.speaker}")
    print("-" * 40)
"""
