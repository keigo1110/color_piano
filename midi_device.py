# デバイス一覧を表示
import pygame.midi

pygame.midi.init()
for i in range(pygame.midi.get_count()):
    interf, name, input, output, opened = pygame.midi.get_device_info(i)
    print(f"ID: {i}, Name: {name.decode()}, Input: {input}, Output: {output}, Opened: {opened}")
pygame.midi.quit()
