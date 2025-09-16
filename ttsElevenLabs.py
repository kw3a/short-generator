import requests
import json
import base64

from subtitles import charsToSubtitles

voices = {
    "spanish": "15bJsujCI3tcDWeoZsQP",
    "english": "cgSgspJ2msm6clMCkdW9",
}

def getVoiceId(language):
    return voices[language]

def ttsElevenLabs(text, voice_id, xi_api_key, audio_file):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"

    headers = {
      "Content-Type": "application/json",
      "xi-api-key": xi_api_key
    }

    data = {
      "text": text,
      "model_id": "eleven_multilingual_v2",
      "voice_settings": {
        "stability": 1,
        "similarity_boost": 0.75
      }
    }


    response = requests.post(
        url,
        json=data,
        headers=headers,
    )

    if response.status_code != 200:
      print(f"Error encountered, status: {response.status_code}, "
              f"content: {response.text}")
      quit()

    json_string = response.content.decode("utf-8")

    response_dict = json.loads(json_string)

    audio_bytes = base64.b64decode(response_dict["audio_base64"])

    with open(audio_file, 'wb') as f:
      f.write(audio_bytes)

    print(response_dict['alignment'])
    return response_dict['alignment']

def test():
    VOICE_ID = voices["spanish"]
    YOUR_XI_API_KEY = ""
    audio_file = "elevenlabs.wav"
    text = """
    uno dos tres
    """
    chars = ttsElevenLabs(text, VOICE_ID, YOUR_XI_API_KEY, audio_file)
    lines = charsToSubtitles(chars)
    print("Subtitles:")
    print(lines)

if __name__ == "__main__":
    test()
