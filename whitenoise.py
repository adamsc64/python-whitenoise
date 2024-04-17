#!/usr/bin/env python3
"""
Plays white noise while running.

Installation:
$ pip install simpleaudio pydub click
"""

import argparse
import datetime
import time
import os
import select
import sys

from pydub import AudioSegment
from simpleaudio._simpleaudio import SimpleaudioError
import simpleaudio
import click


AUDIOFILE = "media/white_noise_10_seconds.wav"
CYCLE_SECONDS = 7
DEFAULT_VOLUME_OFFSET = -7 - 5
CMD_VOL_UP = {"", "+", "="}
CMD_VOL_DOWN = {"-"}
PROMPT = """
python-whitenoise
-----------------
'+' - increase volume
'-' - decrease volume
"""


def play(seg):
    while True:
        try:
            return simpleaudio.play_buffer(
                seg.raw_data,
                num_channels=seg.channels,
                bytes_per_sample=seg.sample_width,
                sample_rate=seg.frame_rate,
            )
        except SimpleaudioError:
            time.sleep(1)


@click.command()
@click.option("--minutes", default=None, help="for how many minutes")
@click.option("--volume", default=0, help="volume modification +/-")
def main(minutes, volume):
    "Play white noise to default audio output device."
    print_prompt()
    return play_noise(minutes=minutes, volume=volume)


def print_prompt():
    print(PROMPT.strip())


def play_noise(minutes, volume):
    start = datetime.datetime.utcnow()
    if minutes:
        minutes = int(minutes)
        stop = start + datetime.timedelta(minutes=minutes)
    else:
        stop = None
    noise = AudioSegment.from_mp3(get_audio_filename())
    noise += DEFAULT_VOLUME_OFFSET + volume
    try:
        playback = play(noise)  # nonblocking
        while (not stop) or (datetime.datetime.utcnow() < stop):
            end_time = time.time() + CYCLE_SECONDS
            while end_time > time.time():
                time.sleep(0.01)  # Prevents process from taking 100% CPU!
                while select.select([sys.stdin.fileno()], [], [], 0.0)[0]:
                    command = os.read(sys.stdin.fileno(), 4096)
                    command = command.decode().strip()
                    for each in command:
                        if each in CMD_VOL_UP:
                            volume += 1
                            noise += 1
                            end_time = 0
                        elif each in CMD_VOL_DOWN:
                            volume -= 1
                            noise -= 1
                            end_time = 0
                    if command:
                        print(f"volume is {volume}")
            old_playback = playback
            old_playback.stop()
            playback = play(noise)  # nonblocking
    except KeyboardInterrupt:
        sys.stdout.flush()
        return True


def get_audio_filename():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), AUDIOFILE)


if __name__ == "__main__":
    main()
