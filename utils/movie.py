import multiprocessing
import os
import random
import praw
import shutil

from pytube import YouTube
from pytube.cli import on_progress
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, TextClip, CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

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
        rand_time = random.randrange(180, int(youtube_length) - int(clip_length))
        return rand_time, rand_time + clip_length

    def download_video(self, video_uri: str, filename: str):
        YouTube(video_uri, on_progress_callback=on_progress, on_complete_callback=print_substep("Video download complete!", style="bold green")).streams.filter(res="1080p").first().download(f"downloaded", filename=filename)

    def generate_footage(self, start_time: int, end_time: int, filename: str):
        print_substep("Generating background clip...", style="bold blue")

        with VideoFileClip(fr"{os.getcwd()}/downloaded/{filename}") as f:
            new = f.subclip(start_time, end_time)
            new.write_videofile("background.mp4")
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

    def make_background(self, clip_length: int):
        # If video is not downloaded, download it
        filename = "minecraft_full_background_1080p.mp4"
        minecraft_uri = "https://www.youtube.com/watch?v=n_Dv4JMiwK8&t"

        if os.path.exists(fr"downloaded\{filename}"):
            print_substep("--------------------------------", style="blue")
            print_substep("Background video already exists!", style="bold green")
            print_substep("--------------------------------", style="blue")
            pass
        else:
            print_step("Background video not downloaded, now downloading. This only needs to happen once and will take a moment...")
            self.download_video(minecraft_uri, filename)

        start_time, end_time = self.get_random_time(clip_length, YouTube(minecraft_uri).length)

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

        audio_clip = AudioFileClip(f"audio/{submission.id}_voice.mp3")

        print_substep(f"Video will be: {length} seconds long", style="bold green")

        image_clips = []

        new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)

        get_screenshots(submission)

        screenshot_width = int((width * 90 ) // 100)
        image_clips.insert(
            0,
            ImageClip(f"screenshots/{submission.id}/png/story_content.png")
            .set_duration(audio_clip.duration)
            .resize(width=screenshot_width)
            .set_opacity(new_opacity)
            .set_position(("center", "center"))
            .set_audio(audio_clip)
        )

        final = CompositeVideoClip([background_clip, image_clips[0]])

        filename = f"FINAL-{submission.id}"

        if not os.path.exists(f"results/{submission.subreddit}"):
            print_substep(f"Results folder for subreddit: {submission.subreddit} does not exists. Creating it now...", style="blue")
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