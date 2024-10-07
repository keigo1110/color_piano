'''GUIでピアノを操作する完成版'''
import pygame
import mido
import time

# MIDIの初期化
def init_midi():
    outport = mido.open_output('IAC Driver')  # 仮想MIDIデバイスのIDを指定
    return outport

# キーを表すクラス
class Key:
    def __init__(self, note, rect, color, is_black, velocity=100):
        self.note = note
        self.rect = rect
        self.color = color
        self.base_color = color
        self.pressed_color = (200, 200, 200) if not is_black else (50, 50, 50)
        self.is_pressed = False
        self.is_black = is_black
        self.velocity = velocity

    def draw(self, screen):
        color = self.pressed_color if self.is_pressed else self.base_color
        pygame.draw.rect(screen, color, self.rect)
        if not self.is_black:
            pygame.draw.rect(screen, (0, 0, 0), self.rect, 1)

    def press(self, midiout):
        if not self.is_pressed:
            midiout.send(mido.Message('note_on', note=self.note, velocity=self.velocity))
            self.is_pressed = True
            print(f"Key {self.note} pressed.")

    def release(self, midiout):
        if self.is_pressed:
            midiout.send(mido.Message('note_off', note=self.note, velocity=0))
            self.is_pressed = False
            print(f"Key {self.note} released.")

# ピアノの鍵盤を設定
def create_piano_keys():
    keys = []
    white_key_notes = [60, 62, 64, 65, 67, 69, 71]  # C4 (60) からの白鍵
    black_key_notes = [61, 63, 66, 68, 70]  # 黒鍵

    key_width = 40
    key_height = 200
    black_key_width = 25
    black_key_height = 120

    for i, note in enumerate(white_key_notes):
        rect = pygame.Rect(i * key_width, 0, key_width, key_height)
        key = Key(note, rect, (255, 255, 255), is_black=False)
        keys.append(key)

    black_key_positions = {
        61: key_width - black_key_width // 2,
        63: 2 * key_width - black_key_width // 2,
        66: 4 * key_width - black_key_width // 2,
        68: 5 * key_width - black_key_width // 2,
        70: 6 * key_width - black_key_width // 2
    }

    for note in black_key_notes:
        x = black_key_positions[note]
        rect = pygame.Rect(x, 0, black_key_width, black_key_height)
        key = Key(note, rect, (0, 0, 0), is_black=True)
        keys.append(key)

    keys.sort(key=lambda k: k.is_black)  # 黒鍵を先に描画
    return keys

# メインのGUI関数
def piano_gui():
    pygame.init()
    screen = pygame.display.set_mode((7 * 40, 200))
    pygame.display.set_caption("MIDI Piano")

    midiout = init_midi()
    keys = create_piano_keys()
    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos
                    for key in reversed(keys):
                        if key.rect.collidepoint(mouse_pos):
                            key.press(midiout)
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_pos = event.pos
                    for key in keys:
                        if key.is_pressed and key.rect.collidepoint(mouse_pos):
                            key.release(midiout)

        for key in keys:
            key.draw(screen)

        pygame.display.update()
        clock.tick(60)

    midiout.close()
    pygame.quit()

if __name__ == "__main__":
    piano_gui()
