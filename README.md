# RedditBot
The RedditBot searches the watchlisted subreddits and picks out an assortment of posts given the filters upon running the bot.

Once the posts have been retrieved, the bot will take the text and convert it to speech (TTS) using the voices found in the audio/samples folder.

Upon conversion to speect, a background video will be downloaded from YouTube, if not already downloaded. If already downloaded, that video will be used.

The video will be clipped to the duration of the TTS and the original source text will be automatically overlayed on the video as those words are spoken in the TTS.

The determination of when the speech occurs/when to display what text and when is done by taking the starting timestamp of a chunk of speech, identifying the word at that timestamp, and matching it to the source text.
The same is then done for the end timestamp of that chunk of TTS and the matching word is found and that becomes the text that is shown on the screen for the duration of the end timestamp - start timestamp.

*NOTE*
- Credentials in the files are old, they don't work anymore.
- The project may not work anymore due to Reddit's API no longer being free
