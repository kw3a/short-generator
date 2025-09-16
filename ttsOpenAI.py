
from openai import OpenAI


def TTSOpenAI(openaiClient, text, voice, audio_file):
    model = "tts-1-hd"
    response = openaiClient.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
    )

    response.stream_to_file(audio_file)

def test():
    OPENAI_API_KEY=""
    client = OpenAI(api_key=OPENAI_API_KEY)
    voice = "nova"
    file_name = f"openai_tts_{voice}_spanish.mp3"
    text = """
    uno dos tres
        """
    TTSOpenAI(client, text, voice, file_name)

if __name__ == "__main__":
    test()


