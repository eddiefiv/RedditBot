import multiprocessing
import os
import random
import praw
import shutil
import textwrap
import json
import wave

from pytube import YouTube
from pytube.cli import on_progress
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, TextClip, CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from vosk import Model, KaldiRecognizer, SetLogLevel

from utils.word import Word
from utils.console import print_step, print_substep
from utils.screenshots import get_screenshots
from utils.video import Video

class Movie:
    def __init__(self, dir):
        os.chdir(dir)

    def set_submission(self, submission):
        self.submission = submission

    def get_random_time(self, clip_length: int, youtube_length: int):
        """Generates a random interval of time to be used as the background of the video.
        Args:
            clip_length (int): Desired length of the final clip
            youtube_length (int): Length of the full background video from YouTube
        Returns:
            tuple(int, int): Randomized start and end time
        """
        rand_time = random.randrange(300, int(youtube_length) - int(clip_length))
        return rand_time, rand_time + clip_length

    def download_video(self, video_uri: str, filename: str):
        try:
            YouTube(video_uri, on_progress_callback=on_progress).streams.filter(res="1080p").first().download(f"downloaded", filename=filename)
            print_substep("Video download complete!", style="bold green")
        except:
            print_substep("Background video download failed. Quitting...", style="red")

    def generate_footage(self, start_time: int, end_time: int, filename: str):
        print_substep("Generating background clip...", style="bold blue")

        try:
            ffmpeg_extract_subclip(
                f"{os.getcwd()}/downloaded/{filename}",
                start_time,
                end_time,
                targetname="background.mp4"
            )
        except (OSError, IOError):
            print_substep("FFMPEG error, trying again...", style="red")
            with VideoFileClip(fr"{os.getcwd()}/downloaded/{filename}") as f:
                new = f.subclip(start_time, end_time)
                new.write_videofile("background.mp4")
        finally:
            if os.path.exists(f"cut_clips/{self.submission.id}"):
                pass
            else:
                os.makedirs(f"cut_clips/{self.submission.id}")

            shutil.move("background.mp4", f"cut_clips/{self.submission.id}/background.mp4")

    def prepare_background(self, width: int, height: int) -> VideoFileClip:
        """
        Crops the background to the given Width and Height to get it ready for production
        """
        clip = (VideoFileClip(f"cut_clips/{self.submission.id}/background.mp4")).without_audio().resize(height=height)

        # Calculate the center
        c = clip.w // 2

        # Calculate the coordinates where to crop
        half_w = width // 2
        x1 = c - half_w
        x2 = c + half_w

        return clip.crop(x1=x1, y1=0, x2=x2, y2=height)

    def make_background(self, clip_length: int, clip: str):
        # If video is not downloaded, download it
        if clip == "Minecraft":
            filename = "minecraft_full_background_1080p.mp4"
            uri = "https://www.youtube.com/watch?v=n_Dv4JMiwK8&t"
        elif clip == "Rocket League":
            filename = "rocket_full_background_1080p.mp4"
            uri = "https://www.youtube.com/watch?v=riilLCDgf-s"
        elif clip == "Subway Surfers":
            filename = "subsurf_full_background_1080p.mp4"
            uri = "https://www.youtube.com/watch?v=dvjy6V4vLlI"
        elif clip == "GTA":
            filename = "gta_full_background_1080p.mp4"
            uri = "https://www.youtube.com/watch?v=vVJuMq1CMNo&t"

        if os.path.exists(fr"downloaded\{filename}"):
            print_substep("--------------------------------", style="blue")
            print_substep("Background video already exists!", style="bold green")
            print_substep("--------------------------------", style="blue")
            pass
        else:
            print_substep("--------------------------------", style="blue")
            print_substep(f"Background video for {clip} is not downloaded yet, now downloading. This will only happen once and may take a moment...", style="bold blue")
            print_substep("--------------------------------", style="blue")
            self.download_video(uri, filename)

        start_time, end_time = self.get_random_time(clip_length, YouTube(uri).length)

        self.generate_footage(start_time, end_time, filename)

    def make_final(self, submission, length: int, width: int, height: int):
        """
        Gathers audio clips, gathers all screenshots, stitches them together and saves the final video to assets/temp
        """
        print_step("Creating the final edit.")

        VideoFileClip.reW = lambda clip: clip.resize(width=width)
        VideoFileClip.reH = lambda clip: clip.resize(width=height)

        opacity = .9

        background_clip = self.prepare_background(width=width, height=height)

        # Audio clip gathering and concatenation
        audio_clips = [AudioFileClip(f"audio/gen/{submission.id}_title_voice.mp3")]
        audio_clips.insert(1, AudioFileClip(f"audio/gen/{submission.id}_voice.mp3"))

        audio_concat = concatenate_audioclips(audio_clips)
        audio_composite = CompositeAudioClip([audio_concat])

        print_substep(f"Video will be: {length} seconds long", style="bold green")

        # Do text chunking
        chunks = textwrap.wrap(submission.selftext.lower(), 80)
        timestamps = [audio_clips[0].duration]
        text_clips = []

        # Use AI model to locate words in the generated tts file
        model_path = "utils/vosk-model-en-us-0.21"
        audio_filename = f"audio/gen/conv/{submission.id}_voice.wav"

        print_substep(f"Compiling speech recognition data", style="bold blue")

        model = Model(model_path)
        wf = wave.open(audio_filename, "rb")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        # Get the list of JSON dictionaries
        results = []

        # Recognize speech using vosk model
        while True:
            data = wf.readframes(4000)
            if (len(data) == 0):
                break
            if rec.AcceptWaveform(data):
                part_result = json.loads(rec.Result())
                results.append(part_result)

        part_result = json.loads(rec.FinalResult())
        results.append(part_result)

        # Convert list of JSON dictionaries to list of 'Word' objects
        list_of_words = []
        list_of_word_strings = []

        for sentence in results:
            if len(sentence) == 1:
                continue
            for obj in sentence['result']:
                w = Word(obj)
                list_of_words.append(w)

        wf.close() # Close audiofile

        # Output to the screen
        for word in list_of_words:
            print(word.to_string())
            list_of_word_strings.append(word.get_word())

        # Generate and add TextClips to the screen
        idx_offset = 0
        title_offset = audio_clips[0].duration
        for i in range(len(chunks)):
            chunk_words = chunks[i].lower().split()
            starting_word_idx = list_of_word_strings.index(chunk_words[0], idx_offset)
            last_word_idx = starting_word_idx + len(chunk_words) - 2
            starting_time = list_of_words[starting_word_idx].get_start() + title_offset
            ending_time = list_of_words[last_word_idx].get_end() + title_offset

            print(f"Chunk: {chunks[i]}\nStarting word and time: {list_of_word_strings[starting_word_idx]}, {starting_time}\nEnding word and time: {list_of_word_strings[last_word_idx]}, {ending_time}")

            txt = TextClip(txt=chunks[i], size=(1080, 720), fontsize=80, font='Segoe-UI-Bold', method='caption', color='white', interline=-1, stroke_color="black", stroke_width=5)
            txt = txt.set_position(("center", "center"))
            txt = txt.set_start(starting_time)
            txt = txt.set_duration(ending_time - starting_time)
            text_clips.append(txt)

            idx_offset = last_word_idx

        # Image clip gathering and concatenation
        image_clips = []

        new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)

        get_screenshots(submission)

        screenshot_width = int((width * 90 ) // 100)
        image_clips.insert(
            0,
            ImageClip(f"screenshots/{submission.id}/png/title.png")
            .set_duration(audio_clips[0].duration)
            .resize(width=screenshot_width)
            .set_opacity(new_opacity)
            .crossfadein(1)
            .crossfadeout(1)
            .set_audio(audio_clips[0])
        )
        image_clips.insert(
            1,
            ImageClip(f"screenshots/{submission.id}/png/story_content.png")
            .set_duration(audio_clips[1].duration)
            .resize(width=screenshot_width)
            .set_opacity(0)
            .set_audio(audio_clips[1])
        )

        image_concat = concatenate_videoclips(image_clips).set_position(("center", "center"))

        #final = CompositeVideoClip([background_clip, image_concat], use_bgclip=True)
        final = CompositeVideoClip([background_clip, image_concat, *text_clips], use_bgclip=True)

        filename = f"FINAL-{submission.id}"

        if not os.path.exists(f"results/{submission.subreddit}"):
            print_substep(f"Results folder for subreddit: {submission.subreddit} does not exist. Creating it now...", style="blue")
            os.makedirs(f"results/{submission.subreddit}")
            print_substep("Folder created!", style="bold green")

        final = Video(final).add_watermark(
            text="Background credit: ----",
            opacity=.4,
            submission=submission
        )

        final.write_videofile(
            filename=f"results/{submission.subreddit}/{filename}.mp4",
            fps=60,
            audio_codec="aac",
            audio_bitrate="192k",
            threads=multiprocessing.cpu_count()
        )