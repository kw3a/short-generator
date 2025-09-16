import requests, base64, random, argparse, os, time, re, textwrap

API_BASE_URL = f"https://api16-normal-v6.tiktokv.com/media/api/text/speech/invoke/"
USER_AGENT = f"com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; Build/NRD90M;tt-ok/3.12.13.1)"


def tts(session_id , voice, text, filename):
    text = text.replace("+", "plus")
    text = text.replace(" ", "+")
    text = text.replace("&", "and")
    text = text.replace("ä", "ae")
    text = text.replace("ö", "oe")
    text = text.replace("ü", "ue")
    text = text.replace("ß", "ss")

    r = requests.post(
        f"{API_BASE_URL}?text_speaker={voice}&req_text={text}&speaker_map_type=0&aid=1233",
        headers={
            'User-Agent': USER_AGENT,
            'Cookie': f'sessionid={session_id}'
        }
    )

    if r.json()["message"] == "Couldn't load speech. Try again.":
        output_data = {"status": "Session ID is invalid", "status_code": 5}
        print(output_data)
        return output_data

    vstr = [r.json()["data"]["v_str"]][0]
    msg = [r.json()["message"]][0]
    scode = [r.json()["status_code"]][0]
    log = [r.json()["extra"]["log_id"]][0]

    dur = [r.json()["data"]["duration"]][0]
    spkr = [r.json()["data"]["speaker"]][0]

    b64d = base64.b64decode(vstr)

    with open(filename, "wb") as out:
        out.write(b64d)

    output_data = {
        "status": msg.capitalize(),
        "status_code": scode,
        "duration": dur,
        "speaker": spkr,
        "log": log
    }

    print(output_data)

    return output_data


def batch_create(filename: str = 'voice.mp3'):
    out = open(filename, 'wb')

    def sorted_alphanumeric(data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(data, key=alphanum_key)

    for item in sorted_alphanumeric(os.listdir('./batch/')):
        filestuff = open('./batch/' + item, 'rb').read()
        out.write(filestuff)

    out.close()

def TTSTiktok(session_id, voice, text, filename):
    chunk_size = 200
    textlist = textwrap.wrap(text, width=chunk_size, break_long_words=True, break_on_hyphens=False)

    batch_dir = './batch/'

    if not os.path.exists(batch_dir):
        os.makedirs(batch_dir)

    for i, item in enumerate(textlist):
        tts(session_id, voice, item, f'{batch_dir}{i}.mp3')

    batch_create(filename)

    for item in os.listdir(batch_dir):
        os.remove(batch_dir + item)

    if os.path.exists:
        os.removedirs(batch_dir)

if __name__ == "__main__":
    voice = "en_us_002"
    text = "Hello world"
    filename = "voice.mp3"
    session = ""
    TTSTiktok(session, voice, text, filename)


