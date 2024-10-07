import mido
import time

outport = mido.open_output('IAC Driver')

notes = [60, 62, 64, 65, 67, 69, 71, 72]  # ドレミファソラシド

for note in notes:
    msg_on = mido.Message('note_on', note=note, velocity=64)
    outport.send(msg_on)
    time.sleep(0.5)
    msg_off = mido.Message('note_off', note=note, velocity=64)
    outport.send(msg_off)
    time.sleep(0.1)
