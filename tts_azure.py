import azure.cognitiveservices.speech as speechsdk

speech_key = ""
service_region = "eastus2"
voice = "es-MX-JorgeNeural"
filename = "azureTTS.wav"
word_timestamps = []

voices = {
        'spanish': 'es-MX-JorgeNeural',
        'english': 'en-US-KaiNeural',
}
def getAzureVoice(language):
    return voices[language]

def speech_synthesizer_word_boundary_cb(evt: speechsdk.SpeechSynthesisWordBoundaryEventArgs):
    print('WordBoundary event:')
    print('\tBoundaryType: {}'.format(evt.boundary_type))
    print('\tAudioOffset: {}ms'.format((evt.audio_offset + 5000) / 10000))
    print('\tDuration: {}'.format(evt.duration))
    print('\tText: {}'.format(evt.text))
    print('\tTextOffset: {}'.format(evt.text_offset))
    print('\tWordLength: {}'.format(evt.word_length))
    if evt.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Word:
        global word_timestamps
        word = evt.text
        start = evt.audio_offset
        start = start * 1e-7
        start = round(start, 3)
        duration = evt.duration
        duration = duration.total_seconds()
        timestamp = {'word': word, 'start': start, 'duration': duration}
        word_timestamps.append(timestamp)

def TTSAzure(azure_key: str, azure_region: str, text: str, voice: str, file_name: str) -> list:
    global word_timestamps
    word_timestamps = []
    speech_config: speechsdk.SpeechConfig = speechsdk.SpeechConfig(subscription=azure_key, region=azure_region)
    speech_config.speech_synthesis_voice_name = voice
    speech_config.request_word_level_timestamps()

    audio_config: speechsdk.audio.AudioOutputConfig = speechsdk.audio.AudioOutputConfig(filename=file_name)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesizer.synthesis_word_boundary.connect(speech_synthesizer_word_boundary_cb)

    result = speech_synthesizer.speak_text(text)

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesis succeeded. The audio was saved to file: " + file_name)
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    return word_timestamps


if __name__ == "__main__":
    """
    subs = TTSAzure(speech_key, service_region, "Hola, este es Jorge.", voice, filename)
    print(subs)
        """
    v = getAzureVoice("english")
    f = "azureTTSenglishmulti.wav"
    subs = TTSAzure(speech_key, service_region, "Hello, this is Ava.", v, f)
    print(subs)

