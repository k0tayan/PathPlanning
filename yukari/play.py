# -*- coding: utf-8 -*-
from pydub import AudioSegment
from pydub.playback import play
import glob
import threading
import simpleaudio


def _play_with_simpleaudio(seg):
    return simpleaudio.play_buffer(
        seg.raw_data,
        num_channels=seg.channels,
        bytes_per_sample=seg.sample_width,
        sample_rate=seg.frame_rate
    )


def start_thread(func, arg):
    thread = threading.Thread(target=func, args=([arg]), daemon=True)
    thread.start()

path = ''
file = AudioSegment.from_file(path, 'wav')

# start_thread(_play_with_simpleaudio, file)
playback = _play_with_simpleaudio(file)
# play(file)

while True:
    num = int(input())
    print(num)
    if num == 1:
        playback.stop()
    if num == 2:
        playback.wait_done()
    if num == 3:
        print(playback.is_playing())
