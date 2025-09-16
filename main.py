from datetime import datetime
import os

from ttsAzure import TTSAzure, getAzureVoice

from videoEdition import add_subtitles_to_video, buildClip
from constants import Config


def dateSanitize():
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")
    return formatted_date

def createVideo(config: Config, title, text, language, filename):
    print(f"Processing submission: {title}")

    target_path = os.path.join(config.OUTPUT_DIR, language)

    os.makedirs(target_path, exist_ok=True)
    print("target directory: ", target_path)
    audio_file = filename + ".mp3"
    output_file = filename + ".mp4"
    audio_file = os.path.join(target_path, audio_file)
    output_file = os.path.join(target_path, output_file)

    voice_id = getAzureVoice(language)
    subs = TTSAzure(config.AZURE_KEY, config.AZURE_REGION, text, voice_id, audio_file)
    print(f"Subtitles length: {len(subs)}")

    clip = buildClip(config.VIDEO_FILE, audio_file)
    add_subtitles_to_video(clip, subs, output_file)

def get_content_from_txt(config: Config, directory: str):
    txt_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                filepath = os.path.join(root, file)
                text = ""
                with open(filepath, "r") as f:
                    text = f.read()
                without_ext = os.path.splitext(file)[0]
                id = without_ext.rstrip("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
                language = without_ext[len(id):]
                if text != "" and language in config.LANGUAGES:
                    txt_files.append({"filename": without_ext, "language": language, "text": text})
    print(f"Found {len(txt_files)} txt files.")
    return txt_files

def main():
    config = Config()
    content_dir = os.path.join(config.OUTPUT_DIR, config.CONTENT_DIR)
    submissions_list = get_content_from_txt(config, content_dir)

    for index, submission in enumerate(submissions_list):
        first_line = submission['text'].split("\n")[0]
        text_length = len(submission['text'])
        words_aprox = text_length // 5
        minutes = words_aprox / 180
        minutes = round(minutes, 2)
        print(f"{index}: [{minutes}] {first_line} | {submission['filename']} ")

    k = input("Press enter to confirm or other key to exit: ")
    if k != "":
        return

    print("Processing submissions...")

    for index, submission in enumerate(submissions_list):
        title = submission['text'].split("\n")[0]
        text = submission['text']
        filename = submission['filename']
        language = submission['language']
        createVideo(config, title, text, language, filename)

    
if __name__ == "__main__":
    main()

