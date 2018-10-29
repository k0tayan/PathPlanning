# -*- coding: utf-8 -*-
from pydub import AudioSegment
import glob
import threading
import simpleaudio

dir = './yukari/files/'
if __name__ == '__main__':
    dir = './files/'

detecting_table_0 = AudioSegment.from_file(dir + 'detecting_table-0.wav', 'wav')
failed_0 = AudioSegment.from_file(dir + 'failed-0.wav', 'wav')
failed_1 = AudioSegment.from_file(dir + 'failed-1.wav', 'wav')
failed_2 = AudioSegment.from_file(dir + 'failed-2.wav', 'wav')
succeed_0 = AudioSegment.from_file(dir + 'succeed-0.wav', 'wav')
succeed_1 = AudioSegment.from_file(dir + 'succeed-1.wav', 'wav')
succeed_2 = AudioSegment.from_file(dir + 'succeed-2.wav', 'wav')
succeed_detecting_table_0 = AudioSegment.from_file(dir + 'succeed_detecting_table-0.wav', 'wav')
info_0 = AudioSegment.from_file(dir + 'info-0.wav', 'wav') # 例外:ホストに到達できません
info_1 = AudioSegment.from_file(dir + 'info-1.wav', 'wav') # ペットボトル判定シーケンスを開始します
info_2 = AudioSegment.from_file(dir + 'info-2.wav', 'wav') # 最短経路計画が終了しました

class Yukari:
    def __init__(self):
        self.playback = None

        self.playable_cant_reach_to_host = True
        self.playable_finish_path_planning = True

    def play(self, seg):
        if self.playback is not None and self.playback.is_playing():
            self.playback.stop()
        self.playback = simpleaudio.play_buffer(
            seg.raw_data,
            num_channels=seg.channels,
            bytes_per_sample=seg.sample_width,
            sample_rate=seg.frame_rate
        )

    def play_fail(self, num):
        if num == 0:
            self.play(failed_0)
        elif num == 1:
            self.play(failed_1)
        elif num == 2:
            self.play(failed_2)
        else:
            raise NameError('num is incorrect')

    def play_success(self, num):
        if num == 0:
            self.play(succeed_0)
        elif num == 1:
            self.play(succeed_1)
        elif num == 2:
            self.play(succeed_2)
        else:
            raise NameError('num is incorrect')

    def play_result(self, num, result):
        if result:
            self.play_success(num)
        else:
            self.play_fail(num)

    def _play_results(self, results):
        for result in results:
            self.play_result(result[0], result[1])
            while self.playback.is_playing():
                pass

    def play_results(self, results):
        # results:
        # [[0, True], [1, False]]
        thread = threading.Thread(target=self._play_results, args=([results]), daemon=True)
        thread.start()


    def play_detecting_table(self):
        self.play(detecting_table_0)

    def play_succeed_detecting_table(self):
        self.play(succeed_detecting_table_0)

    def play_cant_reach_to_host(self):
        if self.playable_cant_reach_to_host:
            self.play(info_0)
        self.playable_cant_reach_to_host = False

    def play_move_to_check_standing_sequence(self):
        self.play(info_1)

    def play_finish_path_planning(self):
        if self.playable_finish_path_planning:
            self.play(info_2)
        self.playable_finish_path_planning = False

if __name__ == '__main__':
    yukari = Yukari()
    yukari.play_results([[0, True], [1, False]])
    input()