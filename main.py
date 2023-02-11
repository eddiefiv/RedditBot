import sys
import math
import os
import sys
import praw
import random
import vlc
import shutil

from playsound import playsound
from mutagen.mp3 import MP3
from utils.tts import TikTokTTS, PollyTTS
from utils.movie import Movie
from utils.console import *

posts = []

reddit = praw.Reddit(
    client_id="X7jFbwxYvdL64Q_2gpAs_g",
    client_secret="ziaP5mW-acbIAILCcs9fZesYZoBcFg",
    user_agent="BradHuds78"
)

movie = Movie(os.getcwd())

def get_subissions(subreddit):
    for submission in reddit.subreddit(subreddit).hot(limit=50):
        posts.append(submission)

def randomize_submissions(amount: int) -> list[praw.Reddit.submission]:
    picked = []

    for i in range(amount):
        idx = random.randint(0, len(posts) - 1)

        post = posts[idx]

        picked.append(post)

    return picked

def manual_check(submissions: list[praw.Reddit.submission]) -> praw.Reddit.submission:
    submissions = submissions

    for i in range(len(submissions)):
        print_substep(f'Is "{submissions[i].title}" an acceptable story at {len(submissions[i].selftext)} characters?')
        acceptable: any = input('(y/n)')

        if (acceptable == "y"):
            acceptable = True
            break
        elif (acceptable == "n"):
            acceptable = False

    if acceptable:
        return submissions[i]

def delete_files():
    shutil.rmtree("cut_clips")
    shutil.rmtree("screenshots")

def start_tts(submission) -> int:
    tiktts = TikTokTTS()
    #polly = PollyTTS()

    #pol_client = polly.connectToPolly()
    #polly.speak(polly=pol_client, text="Testing tesing 1 2 3")

    voice = "en_us_006"
    filename = f"audio/{submission.id}_voice.mp3"

    tiktts.run(voice=voice, text=submission.selftext, filename=filename)

    return MP3(filename).info.length

if __name__ == "__main__":
    print_substep("Please pick an initial option: Manual submission input by URL (1), Automatic submission selection (2)", style="blue")
    selection = input()

    if selection == "1":
        print_substep("Please input a valid reddit post URL:", style="blue")
        submission = reddit.submission(url=input())
    elif selection == "2":
        print_substep("Input a subreddit to pick 5 posts from as text form (leave out the r/):")
        get_subissions(input())
        print_substep("Picking submissions...", style="bold green")
        submissions = randomize_submissions(5)
        submission = manual_check(submissions)
    elif selection != "1" or selection != "2":
        print("Not a valid response, quitting...")
        quit()

    print_step(f'"{submission.title}" by: {submission.author.name}')
    length = start_tts(submission)
    movie.set_submission(submission=submission)
    movie.make_background(clip_length=length)
    movie.make_final(submission, length, 1080, 1920)
    print_substep("Removing unneeded files...", style="blue")
    delete_files()
    print_substep("Unneeded files successfully removed!", style="bold green")
    print_step(f"Final render is complete! Video can be found at: {os.getcwd()}/results/FINAL-{submission.id}")