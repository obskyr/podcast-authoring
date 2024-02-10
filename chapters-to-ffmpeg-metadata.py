#!/usr/bin/env python3

"""Turn an Audacity "Label Track.txt" into an FFmpeg metadata file."""

import os
import re
import sys

LABEL_LINE_RE = re.compile(r"^(?P<start>[0-9]+(?:.[0-9]+)?)\s+(?P<end>[0-9]+(?:.[0-9]+)?)\s+(?P<title>.*)$")
def to_ffmetadata(labels_s):
    chapters = []
    for line in labels_s.splitlines():
        line = line.strip()
        if not line:
            continue
        m = LABEL_LINE_RE.match(line)
        if m is None:
            raise ValueError("Malformed label track data.")
        start = float(m.group('start'))
        end = float(m.group('end'))
        title = escape(m.group('title'))
        chapters.append((start, end, title))
    chapters = sorted(chapters, key=lambda t: t[0])

    s = ";FFMETADATA1\n"

    # This is according to https://dbojan.github.io/howto_pc/media,%20How%20to%20add%20chapter%20marks%20to%20audio%20books,%20using%20opus%20codec.htm,
    # but it seems that it doesn't actually work. Judging by a recent FFmpeg
    # issue, https://trac.ffmpeg.org/ticket/7532, Ogg might use the regular
    # [CHAPTER] tags in a future version… perhaps? So this may be a dead end.
    # # For Ogg files.
    # s += "\n"
    # for i, (start, end, title) in enumerate(chapters):
    #     s += f"CHAPTER{i:03}={to_timestamp(start)}\nCHAPTER{i:03}NAME={title}\n"

    # For MPEG-4 files.
    for start, end, title in chapters:
        start = round(start * 1000)
        end = round(end * 1000)
        s += f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={start}\nEND={end}\ntitle={title}\n"

    return s

ESCAPE_RE = re.compile(r"[=;#\n]")
def escape(s):
    return ESCAPE_RE.sub("\\\g<0>", s)

def to_timestamp(seconds):
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:.0f}:{minutes:02.0f}:{seconds:06.3f}"

def main(*argv):
    script_name = os.path.basename(__file__)
    try:
        in_path = argv[0]
    except IndexError:
        print(f"Usage: {script_name} <path to label track TXT> [output path]", file=sys.stderr)
        return 1
    try:
        out_path = argv[1]
    except IndexError:
        out_path = os.path.join(os.path.dirname(in_path), 'ffmetadata.txt')

    with open(in_path, 'r', encoding='utf-8') as f:
        s = f.read()

    s = to_ffmetadata(s)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(s)

    print(f"Successfully wrote chapters from \"{in_path}\" to \"{out_path}\"!")

    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
