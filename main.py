import sys
import math
import os
import praw
import random
import shutil

from time import sleep
from playsound import playsound
from mutagen.mp3 import MP3
from utils.tts import TikTokTTS
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
    print_substep("Picking submissions...", style="bold green")
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
        elif (acceptable == "n"):
            acceptable = False

        if acceptable:
            return submissions[i]

    print_substep("Please pick an initial option: Manual submission input by URL (1), Automatic submission selection (2)", style="blue")

def delete_files():
    shutil.rmtree("cut_clips")
    shutil.rmtree("screenshots")

    for file in os.listdir(f"audio/gen"):
        if file.endswith(".mp3"):
            os.remove(file)

def start_tts(submission, voice, is_title: bool) -> int:
    tiktts = TikTokTTS()
    #polly = PollyTTS()

    #pol_client = polly.connectToPolly()
    #polly.speak(polly=pol_client, text="Testing tesing 1 2 3")

    if os.path.exists("audio/gen"):
        pass
    else:
        os.makedirs("audio/gen")

    if is_title:
        filename = f"audio/gen/{submission.id}_title_voice.mp3"
        text = submission.title
    else:
        filename = f"audio/gen/{submission.id}_voice.mp3"
        text = submission.selftext

    tiktts.run(voice=voice, text=text, filename=filename)

    return MP3(filename).info.length

if __name__ == "__main__":
    print_substep("Please pick an initial option: Manual submission input by URL (1), Automatic submission selection (2)", style="blue")

    while True:
        selection = input()
        if selection == "1":
            try:
                print_substep("Please input a valid Redit post URL:", style="blue")
                submission = reddit.submission(url=input())
                break
            except:
                print_substep("Invalid Reddit submission URL.", style="red")
        elif selection == "2":
            try:
                try:
                    print_substep("Input a Subreddit to pick 10 posts from as text form (leave out the r/):", style="blue")
                    get_subissions(input())
                except:
                    print_substep("Invalid Subreddit.", style="red")
                    sys.exit()
                finally:
                    submissions = randomize_submissions(10)
                    submission = manual_check(submissions)
                    break
            except:
                print_substep("Couldnt pick a submission, try again.", style="red")
        elif selection == "quit" or selection == "exit":
            sys.exit()
        elif selection != "1" or selection != "2":
            print_substep("Not a valid response.", style="red")

    print_step(f'"{submission.title}" by: {submission.author.name}')

    while True:
        print_substep("--------------------------------", style="blue")
        print_substep("Please pick a voice to use or use (Preview) to sample a voice: (Male 1, Male 2, Female 1, Female 2, Narrator, Funny, Peaceful, Serious, Ghost Face)", style="blue")
        voice = input()
        print_substep("--------------------------------", style="blue")

        if voice.lower() == "preview":
            print_substep("Please select a voice to sample", style="blue")
            sample = input()

            if sample.lower() == "male 1":
                playsound("audio/samples/en_us_male1.mp3")
            if sample.lower() == "male 2":
                playsound("audio/samples/en_us_male2.mp3")
            if sample.lower() == "female 1":
                playsound("audio/samples/en_us_female1.mp3")
            if sample.lower() == "female 2":
                playsound("audio/samples/en_us_female2.mp3")
            if sample.lower() == "narrator":
                playsound("audio/samples/en_male_narration.mp3")
            if sample.lower() == "funny":
                playsound("audio/samples/en_male_funny.mp3")
            if sample.lower() == "peaceful":
                playsound("audio/samples/en_female_emotional_voice.mp3")
            if sample.lower() == "serious":
                playsound("audio/samples/en_male_cody_voice.mp3")
            if sample.lower() == "ghost face":
                playsound("audio/samples/en_us_ghostface_voice.mp3")
            if sample.lower() == "quit" or sample.lower() == "exit":
                sys.exit()
        if voice.lower() == "male 1":
            voice = "en_us_006"
            break
        if voice.lower() == "male 2":
            voice = "en_us_007"
            break
        if voice.lower() == "female 1":
            voice = "en_us_001"
            break
        if voice.lower() == "female 1":
            voice = "en_us_002"
            break
        if voice.lower() == "narrator":
            voice = "en_male_narration"
            break
        if voice.lower() == "funny":
            voice = "en_male_funny"
            break
        if voice.lower() == "peaceful":
            voice = "en_female_emotional"
            break
        if voice.lower() == "serious":
            voice = "en_male_cody"
            break
        if voice.lower() == "ghost face":
            voice = "en_us_ghostface"
            break
        if voice.lower() == "quit" or voice.lower() == "exit":
            sys.exit()
        else:
            print_substep("Invalid voice selection", style="red")


    print_substep("Compiling submission title to TTS", style="bold blue")
    title_length = start_tts(submission, voice, True)
    print_substep("Compiling submission text to TTS", style="bold blue")
    story_length = start_tts(submission, voice, False)

    length = title_length + story_length

    movie.set_submission(submission=submission)

    while True:
        print_substep("Choose a background clip to use (Minecraft, Rocket League, Subway Surfers, GTA)", style="blue")
        choice = input()

        if choice.lower() == "minecraft":
            movie.make_background(clip_length=length, clip="Minecraft")
            break
        elif choice.lower() == "rocket league":
            movie.make_background(clip_length=length, clip="Rocket League")
            break
        elif choice.lower() == "subway surfers":
            movie.make_background(clip_length=length, clip="Subway Surfers")
            break
        elif choice.lower() == "gta":
            movie.make_background(clip_length=length, clip="GTA")
            break
        else:
            print_substep("Please pick a valid background video choice.", style="red")

    movie.make_final(submission, length, 1080, 1920)
    print_substep("Removing unneeded files...", style="blue")
    try:
        sleep(2)
        delete_files()
        print_substep("Unneeded files successfully removed!", style="bold green")
    except OSError as e:
        print_substep("Non-Fatal Warning: Could not successfully delete all unnecessary files. Manual deletion may be required.", style="yellow")
        print_substep(f"Failed with: {e.strerror}", style="red")
    finally:
        print_step(f"Final render is complete! Video can be found at: {os.getcwd()}/results/FINAL-{submission.id}")