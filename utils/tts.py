import base64
import requests
import os
import boto3
import re
import textwrap
import elevenlabslib as el
import wave

from typing import Optional, Final

from utils.console import *

__all__ = ["TikTok", "TikTokTTSException"]

defaultRegion = 'us-east-1'
defaultUrl = 'https://polly.us-east-1.amazonaws.com'

elclient = el.ElevenLabsUser("66ea4d1ed826e7fc199c9809467a3fdd")
elvoice = elclient.get_voices_by_name("Josh")[0]

disney_voices: Final[tuple] = (
    "en_us_ghostface",  # Ghost Face
    "en_us_chewbacca",  # Chewbacca
    "en_us_c3po",  # C3PO
    "en_us_stitch",  # Stitch
    "en_us_stormtrooper",  # Stormtrooper
    "en_us_rocket",  # Rocket
    "en_female_madam_leota",  # Madame Leota
    "en_male_ghosthost",  # Ghost Host
    "en_male_pirate",  # pirate
)

eng_voices: Final[tuple] = (
    "en_au_001",  # English AU - Female
    "en_au_002",  # English AU - Male
    "en_uk_001",  # English UK - Male 1
    "en_uk_003",  # English UK - Male 2
    "en_us_001",  # English US - Female (Int. 1)
    "en_us_002",  # English US - Female (Int. 2)
    "en_us_006",  # English US - Male 1
    "en_us_007",  # English US - Male 2
    "en_us_009",  # English US - Male 3
    "en_us_010",  # English US - Male 4
    "en_male_narration",  # Narrator
    "en_male_funny",  # Funny
    "en_female_emotional",  # Peaceful
    "en_male_cody",  # Serious
)

non_eng_voices: Final[tuple] = (
    # Western European voices
    "fr_001",  # French - Male 1
    "fr_002",  # French - Male 2
    "de_001",  # German - Female
    "de_002",  # German - Male
    "es_002",  # Spanish - Male
    "it_male_m18"  # Italian - Male
    # South american voices
    "es_mx_002",  # Spanish MX - Male
    "br_001",  # Portuguese BR - Female 1
    "br_003",  # Portuguese BR - Female 2
    "br_004",  # Portuguese BR - Female 3
    "br_005",  # Portuguese BR - Male
    # asian voices
    "id_001",  # Indonesian - Female
    "jp_001",  # Japanese - Female 1
    "jp_003",  # Japanese - Female 2
    "jp_005",  # Japanese - Female 3
    "jp_006",  # Japanese - Male
    "kr_002",  # Korean - Male 1
    "kr_003",  # Korean - Female
    "kr_004",  # Korean - Male 2
)

vocals: Final[tuple] = (
    "en_female_f08_salut_damour",  # Alto
    "en_male_m03_lobby",  # Tenor
    "en_male_m03_sunshine_soon",  # Sunshine Soon
    "en_female_f08_warmy_breeze",  # Warmy Breeze
    "en_female_ht_f08_glorious",  # Glorious
    "en_male_sing_funny_it_goes_up",  # It Goes Up
    "en_male_m2_xhxs_m03_silly",  # Chipmunk
    "en_female_ht_f08_wonderful_world",  # Dramatic
)

class TikTokTTS:
    """TikTok Text-to-Speech Wrapper"""
    def __init__(self):
        self.session = requests.Session()
        self.sessionid = "9798f0eb802e0cb2f7a2312a3606e31c"

    def batch_create(self, filename: str = 'voice.mp3'):
        out = open(filename, 'wb')

        def sorted_alphanumeric(data):
            convert = lambda text: int(text) if text.isdigit() else text.lower()
            alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
            return sorted(data, key=alphanum_key)

        for item in sorted_alphanumeric(os.listdir('./batch/')):
            filestuff = open('./batch/' + item, 'rb').read()
            out.write(filestuff)

        out.close()

    def reg_tts(self, voice: str, text: str, filename: str):
        text = text.replace("+", "plus")
        text = text.replace(" ", "+")
        text = text.replace("&", "and")

        headers = {
            "User-Agent": "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; Build/NRD90M;tt-ok/3.12.13.1)",
            "Cookie": f"sessionid={self.sessionid}",
        }

        r = requests.post(f"https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke/?text_speaker={voice}&req_text={text}&speaker_map_type=0&aid=1233", headers=headers)

        if r.json()['message'] == "Couldn't load speech. Try again.":
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
            out.close()

        output_data = {
            "status": msg.capitalize(),
            "status_code": scode,
            "duration": dur,
            "speaker": spkr,
            "log": log
        }

        print_substep(output_data, style="green")

        return output_data

    def tts_batch(self, voice: str, text: str, filename: str):
        text = text.replace("+", "plus")
        text = text.replace(" ", "+")
        text = text.replace("&", "and")

        headers = {
                "User-Agent": "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; Build/NRD90M;tt-ok/3.12.13.1)",
                "Cookie": f"sessionid={self.sessionid}",
            }

        r = requests.post(f"https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke/?text_speaker={voice}&req_text={text}&speaker_map_type=0&aid=1233", headers=headers)

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
            out.close()

        output_data = {
            "status": msg.capitalize(),
            "status_code": scode,
            "duration": dur,
            "speaker": spkr,
            "log": log
        }

        print_substep(output_data, style="green")

        return output_data

    def run(self, voice: str, text: str, filename: str):
        if len(text) <= 200:
            self.reg_tts(voice, text, filename)
        else:
            chunk_size = 200
            textlist = textwrap.wrap(text, width=chunk_size, break_long_words=True, break_on_hyphens=False)

            os.makedirs('./batch/')

            for i, item in enumerate(textlist):
                self.tts_batch(voice, item, f'./batch/{i}.mp3')

            self.batch_create(filename)

            for item in os.listdir('./batch/'):
                os.remove('./batch/' + item)

            os.removedirs('./batch/')

            return

class ElevenLabsTTS:
    def __init__(self):
        self.voice = elvoice
        self.client = elclient

    def run(self, text, filename):
        bytes = self.voice.generate_audio_bytes(text)

        with open(filename, 'wb') as file:
            file.write(bytes)
            file.close()

        for historyItem in self.client.get_history_items():
            if historyItem.text == text:
                # The first items are the newest, so we can stop as soon as we find one.
                historyItem.delete()
                break

class PollyTTS:
    def __init__(self):
        self.default_region = defaultRegion
        self.default_url = defaultUrl

    def connectToPolly(self):
        return boto3.client('polly', region_name=self.default_region, endpoint_url=self.default_url)

    def speak(self, polly, text: str, format: str ="mp3", voice: str = "Brian"):
        response = polly.synthesize_speech(OutputFormat=format, Text=text, VoiceId=voice)
        with open('voice.mp3' 'w') as file:
            soundbytes = response['AudioStream'].read()
            file.write(soundbytes)
            file.close()