# デバイス一覧を表示
import pygame.midi

def list_midi_devices():
    pygame.midi.init()
    device_count = pygame.midi.get_count()
    for i in range(device_count):
        interf, name, is_input, is_output, opened = pygame.midi.get_device_info(i)
        if is_output:
            print(f"デバイスID {i}: '{name.decode()}'")
            
pygame.midi.init()
for i in range(pygame.midi.get_count()):
    interf, name, input, output, opened = pygame.midi.get_device_info(i)
    print(f"ID: {i}, Name: {name.decode()}, Input: {input}, Output: {output}, Opened: {opened}")
    list_midi_devices()
pygame.midi.quit()

