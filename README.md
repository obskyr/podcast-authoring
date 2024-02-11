# Self-authoring podcasts (for free!)

This repository contains a set of self-written tools that I use when authoring my podcasts, as well as notes on the technical side of my process. I primarily keep this repository for my own sake – I don't particularly expect that the tools will be user-friendly enough to be a perfect option for most people, or that the processes will be applicable to everyone's skillsets and needs – but perhaps they could help someone in some way, so why not make it public! Especially worth noting is that this entire stack – including hosting – is entirely *free,* which ain't too shabby in this day and age.

At the time of writing, the tools and processes found here are used to make [Obscuriosities](https://podcast.obskyr.io/). If you, dear reader, would like any advice on podcast authoring or otherwise have any questions, please do hit me up, for example via DM [@obskyr on Twitter.](https://twitter.com/obskyr)

## Tools

* **[`encode.bat`](/encode.bat):** Encode a lossless audio file to the formats used in my podcasts. (You may have different needs, but the parameters found in this file may still serve as a base, and the comments within elucidate why I made some of the decisions I made!)
* **[`chapters-to-ffmpeg-metadata.py`](/encode.bat):** Convert a label file exported from Audacity to an `ffmetadata.txt`, so that chapter marks can be added with FFmpeg.
* **[`crossfade-video.py`](/crossfade-video.py):** String together any number of video clips with a cross-fade effect with FFmpeg.

## Workflow

### Audacity

More or less the same procedure should be usable in most any other audio editing software as well. I *have* been considering migrating to Reaper…

1. Edit speech unprocessed; add music and what have you on separate tracks.
2. Copy the raw speech to a new audio track; mute the original one. (This ensures that your original recording will be available if ever you need to remaster it.)
3. Noise reduction. <!-- 4. De-esser (TDR Nova) (??? Haven't quite figured this one out yet. Can skip. It sounds fine without.) -->
4. Compression, step 1: Drop peaks. (I've been using [TDR Kotelnikov](https://www.tokyodawn.net/tdr-kotelnikov/) for this.)
5. Equalization. (I've been using [TDR Nova](https://www.tokyodawn.net/tdr-nova/) for this.)
6. Compression, step 2: Smooth out. (TDR Kotelnikov here as well.)
7. Loudness normalization to -18 LUFS (it really should be -16, by Apple Podcasts's standards, but I just couldn't compress well enough to make that work without clipping – worth investigating further).
8. Limiter: Hard limit; -1 dB.
9. <kbd>File</kbd> → <kbd>Export Other</kbd> → <kbd>Export Labels…</kbd> to export chapters. (If you have other label tracks, delete those temporarily while doing this.)
10. Export audio to FLAC.

#### Tips

* To move a clip and all clips after it, select the clip (by clicking the bar on top of it) and press <kbd><kbd>Shift</kbd> + <kbd>K</kbd></kbd> to select to the end. (Make sure sync lock is turned on if you wish to move other tracks with it.) <kbd><kbd>Shift</kbd> + <kbd>End</kbd></kbd> does the same but also jumps the view to the end, and is thus impractical.
* Use [Punch Copy/Paste](https://forum.audacityteam.org/t/punch-copy-paste/28906) to insert room tone instead of silence. Always keeping a bit of room tone in a separate track may be helpful as well.
* If using “Truncate silence” to speed up editing, don't go too hard on it, or you'll cut off breaths unnaturally! A threshold of -40 dB with a minimum duration of 3 seconds, truncating to 1 second, worked for my particular recordings. 

### Encoding

1. Drag-and-drop your label file (containing chapter marks) onto [`chapters-to-ffmpeg-metadata.py`](chapters-to-ffmpeg-metadata.py).
2. Drag-and-drop your FLAC file onto [`encode.bat`](/encode.bat).

### Publishing

The above steps are applicable whatever you may be doing with the files afterward. Here's how I personally publish and host my podcast, however.

* Self-publish the podcast using Jekyll to generate both [the website](https://podcast.obskyr.io/) and the RSS feeds. It's not by any means a plug-and-play solution – more suitable for people who are comfortable writing web front-end code (and perhaps even Ruby, though that's me going beyond the call of duty for minimal gains) – but it gives you full control, is entirely free, and makes you feel like a hearty DIY dad! [The source is available on GitHub](https://github.com/obskyr/obscuriosities) and is libre software, so feel free to fork and redesign it (you can drop in any Jekyll theme, really) to suit your own needs.
* Host both website and audio files on GitHub Pages. *Also* free! [The config for that can be found here.](https://github.com/obskyr/obscuriosities/blob/master/.github/workflows/jekyll-gh-pages.yml) GitHub frowns upon serving too large files to too many people, however, so I aim to eventually migrate at least the audio files to a different service – say, Cloudflare R2? Appears to be cost-effective.
