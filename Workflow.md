
## Audacity

More or less the same procedure should be usable in most any other audio editing software as well. I *have* been considering migrating to Reaper…

1. Edit speech unprocessed; add music and what have you on separate tracks.
2. Copy the raw speech to a new audio track; mute the original one. (This ensures that your original recording will be available if ever you need to remaster it.)
3. Noise reduction. <!-- 4. De-esser (TDR Nova) (??? Haven't quite figured this one out yet. Can skip. It sounds fine without.) -->
4. Compression, step 1: Drop peaks. (I've been using TDR Kotelnikov for this.)
5. Equalization. (I've been using TDR Nova for this.)
6. Compression, step 2: Smooth out. (TDR Kotelnikov here as well.)
7. Loudness normalization to -18 LUFS (it really should be -16, but I just couldn't compress well enough to make that work without clipping – worth investigating further).
8. Limiter: Hard limit; -1 dB.
9. File → Export Other → Export Labels… to export chapters. (If you have other label tracks, delete those temporarily while doing this.)
10. Export audio to FLAC.

### Tips

* To move a clip and all clips after it, select the clip (by clicking the bar on top of it) and press Shift+K to select to the end. (Make sure sync lock is turned on if you wish to move other tracks with it.) Shift+End does the same but also jumps the view to the end, and is thus impractical.
* Use [Punch Copy/Paste](https://forum.audacityteam.org/t/punch-copy-paste/28906) to insert room tone instead of silence. Always keeping a bit of room tone in a separate track may be helpful as well.
* If using “Truncate silence” to speed up editing, don't go too hard on it, or you'll cut off breaths unnaturally! A threshold of -40 dB with a minimum duration of 3 seconds, truncating to 1 second, worked for my particular recordings. 

## Encoding

1. Drag-and-drop your label file (containing chapter marks) onto [`chapters-to-ffmpeg-metadata.py`](chapters-to-ffmpeg-metadata.py).
2. Drag-and-drop your FLAC file onto [`encode.bat`](/encode.bat). (Details about the encoding parameters can be peeped in that file.)
