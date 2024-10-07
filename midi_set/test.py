# ピアノの音を鳴らすテストプログラム
import pygame.midi as m
import time

def main():
    m.init()
    i_num = m.get_count()
    for i in range(i_num):
        print(i)
        print(m.get_device_info(i))

    midiout = m.Output(3) #直前のMIDIポート一覧から仮想デバイスのポート(自分の環境では「IAC Driver My Port」)のIDを確認して、その数値にしてください
    midiout.note_on(60,100)
    time.sleep(1)
    midiout.note_off(60)
    midiout.note_on(64,100)
    time.sleep(1)
    midiout.note_off(64)
    midiout.note_on(67,100)
    time.sleep(1)
    midiout.note_off(67)
    time.sleep(1)
    midiout.note_on(60,100)
    midiout.note_on(64,100)
    midiout.note_on(67,100)
    time.sleep(1)
    midiout.note_off(60,100)
    midiout.note_off(64,100)
    midiout.note_off(67,100)

    midiout.close()
    m.quit()
    exit()

if __name__=="__main__":
    main()
