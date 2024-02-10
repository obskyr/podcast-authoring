#!/usr/bin/env python3

"""Cross-fade together video clips with FFmpeg."""

import os
import re
import sys
import subprocess

from collections import namedtuple
from itertools import chain

FADE_DURATION = 2
FADE_AT_END = False

TIMESTAMP_RE = re.compile(r"^(?:(?P<hours>[0-9]+):)??(?:(?P<minutes>[0-9]+):)??(?P<seconds>[0-9]+(?:\.[0-9]+)?)$")
def _timestamp_to_seconds(s):
    m = TIMESTAMP_RE.match(s)
    return int(m['hours'] or '0') * 3600 + \
           int(m['minutes'] or '0') * 60 + \
           float(m['seconds'])

class VideoFile:
    def __init__(self, path, start, bounds):
        self.path = path
        self.start = start
        self.bounds = bounds
        output = subprocess.check_output((
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration:stream=width,height',
            '-print_format', 'default=noprint_wrappers=1',
            path
        ))
        # No idea what FFprobe does with Unicode characters,
        # but the output for these specific entries is just ASCII anyway.
        output = output.decode('ascii')
        info = dict(line.split('=', 1) for line in output.splitlines())
        if info['duration'] == 'N/A':
            self.has_audio = False
            self.full_duration = None
        else:
            self.has_audio = True
            self.full_duration = float(info['duration'])
        self.duration = self.full_duration
        if bounds[1] is not None:
            self.duration = bounds[1]
        if bounds[0] is not None:
            self.duration -= bounds[0]
        self.resolution = (int(info['width']), int(info['height']))
        self.fade_point = (bounds[1] or ((bounds[0] or 0) + self.duration)) - FADE_DURATION

class Fader:
    def __init__(self, args):
        start = 0
        self._videos = []
        for path, trim_start, trim_end in args:
            trim_start = _timestamp_to_seconds(trim_start) if trim_start is not None else trim_start
            trim_end = _timestamp_to_seconds(trim_end) if trim_end is not None else trim_end
            cur_video = VideoFile(path, start, (trim_start, trim_end))
            self._videos.append(cur_video)
            start += cur_video.duration - FADE_DURATION

    def do(self, output_path):
        command = ['ffmpeg', '-y']
        for video in self._videos:
            # Hrm. This didn't work.
            # if video.bounds != (None, None):
            #     if video.bounds[0] is not None:
            #         command += ['-ss', str(video.bounds[0])]
            #     if video.bounds[1] is not None:
            #         command += ['-to', str(video.bounds[1])]
            if video.full_duration is None:
                command += ['-loop', '1', '-framerate', '25']
            command += ['-i', video.path]
        max_width = max(v.resolution[0] for v in self._videos)
        max_height = max(v.resolution[1] for v in self._videos)
        command += [
            '-f', 'lavfi',
            '-i', f'color=color=black:size={max_width}x{max_height}',
            '-filter_complex', self._get_filter_arg(),
            '-codec:v', 'libx264',
            '-codec:a', 'libfdk_aac',
            '-map', '[outv]',
            '-map', '[outa]',
            output_path
        ]
        # print("\n".join(command[-10].split(';')))
        print(' '.join(part if not re.search(r"[ \[\]]", part) else '"' + part + '"' for part in command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1)
        for x in iter(process.stdout.readline, b''):
            print(x, end='')
        process.stdout.close()
        process.wait()

    def _get_filter_arg(self):
        return self._get_video_filter_arg() + ';' + self._get_audio_filter_arg()

    def _get_audio_filter_arg(self):
        s = ''
        for i, video in enumerate(self._videos):
            if video.bounds == (None, None):
                trim_arg = 'acopy'
            else:
                trim_arg = f'atrim='
                trims = []
                if video.bounds[0] is not None:
                    trims.append(f'start={video.bounds[0]}')
                if video.bounds[1] is not None:
                    trims.append(f'end={video.bounds[1]}')
                trim_arg += ':'.join(trims)
            if video.has_audio:
                s += f'[{i}:a]{trim_arg}[a{i}];'
            else:
                s += f'anullsrc,{trim_arg}[a{i}];'
        for i, video in enumerate(self._videos[:-1]):
            in_1 = f'a{i}' if i == 0 else f'accumulated{i}'
            out = '[outa]' if i == len(self._videos) - 2 else f'[accumulated{i + 1}];'
            s += f'[{in_1}][a{i + 1}]acrossfade=d={FADE_DURATION}:c1=tri:c2=tri{out}'
        return s

    def _get_video_filter_arg(self):
        total_duration = self._videos[-1].start + self._videos[-1].duration
        s = self._get_fades()
        s += f'[{len(self._videos)}:v]trim=duration={total_duration}[over0];'
        s += self._get_overlays()
        return s

    def _get_fades(self):
        s = ''
        last_index = len(self._videos) - 1
        for i, video in enumerate(self._videos):
            s += f'[{i}:v]format=pix_fmts=yuva420p,'
            # Okay, it's not *just* fades - we handle the video trimming here too.
            if video.bounds != (None, None):
                s += 'trim='
                trims = []
                if video.bounds[0] is not None:
                    trims.append(f'start={video.bounds[0]}')
                if video.bounds[1] is not None:
                    trims.append(f'end={video.bounds[1]}')
                s += ':'.join(trims)
                s += ','
            if i != 0:
                s += f'fade=t=in:st={video.bounds[0] or 0}:d={FADE_DURATION}:alpha=1,'
            if FADE_AT_END or i != last_index:
                s += f'fade=t=out:st={video.fade_point}:d={FADE_DURATION}:alpha=1,'
            s += 'setpts=PTS-STARTPTS'
            if i != 0:
                s += f'+{video.start}/TB'
            s += f'[v{i}];'
        return s

    def _get_overlays(self):
        s = ''
        i = 0
        for i in range(len(self._videos[:-1])):
            s += f'[over{i}][v{i}]overlay[over{i + 1}];'
        s += f'[over{i + 1}][v{i + 1}]overlay=format=yuv420[outv]'
        return s

def main(*argv):
    script_name = os.path.basename(__file__)

    output_path = None

    fader_args = []
    args = iter(argv)
    start = None
    end = None
    for arg in args:
        if arg == '-o':
            output_path = next(args)
        elif arg in ('-s', '--start'):
            start = next(args)
        elif arg in ('-e', '--end'):
            end = next(args)
        else:
            fader_args.append((arg, start, end))
            start = None
            end = None

    if len(fader_args) < 2:
        print(f"Usage: {script_name} [-s / --start start time] [-e / --end end time] <paths to video files> [-o output path]", file=sys.stderr)
        return 1

    if output_path is None:
        name, extension = os.path.splitext(fader_args[0][0])
        output_path = f'{name}-combined.mp4'

    fader = Fader(fader_args)
    fader.do(output_path)

    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
