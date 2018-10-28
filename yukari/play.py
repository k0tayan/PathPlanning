# -*- coding: utf-8 -*-
from pydub import AudioSegment
from pydub.playback import play
import glob

files = glob.glob('./*.wav')
# 音声ファイルの読み込み
for file in files:
	sound = AudioSegment.from_file(file, "wav")
	# 再生
	play(sound)