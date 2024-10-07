# キーボードの音をGUI操作で鳴らすが最初の一音目しか鳴らないバグがある
import pygame
import pygame.midi
import time

'''MIDIの初期化'''
def init_midi():
    pygame.midi.init()
    output_id = pygame.midi.get_default_output_id() # 仮想MIDIデバイスのIDに置き換えてください
    return pygame.midi.Output(output_id)

# キーを表すクラス
class Key:
    def __init__(self, note, rect, color, is_black, velocity=100):
        '''
        note: 音符
        rect: 矩形
        color: 色
        is_black: 黒鍵かどうか
        velocity: 音量
        release_time: リリース時間
        release_duration: リリース時間の長さ
        '''
        self.note = note
        self.rect = rect
        self.color = color
        self.base_color = color
        self.pressed_color = (200, 200, 200) if not is_black else (50, 50, 50)
        self.is_pressed = False
        self.is_black = is_black
        self.velocity = velocity
        self.release_time = None
        self.release_duration = 0.5  # 0.5秒でフェードアウト

    def draw(self, screen):
        if self.is_pressed:
            color = self.pressed_color
        elif self.release_time is not None:
            t = min(1, (time.time() - self.release_time) / self.release_duration)
            r = int(self.pressed_color[0] + (self.base_color[0] - self.pressed_color[0]) * t)
            g = int(self.pressed_color[1] + (self.base_color[1] - self.pressed_color[1]) * t)
            b = int(self.pressed_color[2] + (self.base_color[2] - self.pressed_color[2]) * t)
            color = (r, g, b)
        else:
            color = self.base_color

        pygame.draw.rect(screen, color, self.rect) # 矩形を描画
        if not self.is_black:
            pygame.draw.rect(screen, (0, 0, 0), self.rect, 1) # 矩形の枠を描画

    def press(self, midiout):
        if not self.is_pressed:
            midiout.write_short(0x90, self.note, self.velocity) # ノートオン
            self.is_pressed = True
            self.release_time = None
            print(f"Key {self.note} pressed.")

    def release(self, midiout):
        if self.is_pressed:
            midiout.write_short(0x80, self.note, 0) # ノートオフ
            self.is_pressed = False
            self.release_time = time.time()
            print(f"Key {self.note} released.")

    def update(self, midiout):
        if not self.is_pressed and self.release_time is not None:
            t = (time.time() - self.release_time) / self.release_duration
            if t >= 1:
                midiout.write_short(0x80, self.note, 0)
                self.release_time = None
                print(f"Key {self.note} fade-out completed.")

# ピアノの鍵盤を設定
def create_piano_keys():
    keys = []
    white_key_notes = [60, 62, 64, 65, 67, 69, 71]
    black_key_notes = [61, 63, 66, 68, 70]

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

    keys.sort(key=lambda k: k.is_black)
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

            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Left mouse button is held down
                    mouse_pos = event.pos
                    for key in reversed(keys):
                        if key.rect.collidepoint(mouse_pos):
                            if not key.is_pressed:
                                key.press(midiout)
                        elif key.is_pressed:
                            key.release(midiout)

        for key in keys:
            key.update(midiout)
            key.draw(screen)

        pygame.display.update()
        clock.tick(60)  # Limit the frame rate to 60 FPS

    # すべての音を停止
    for key in keys:
        midiout.write_short(0x80, key.note, 0)

    midiout.close()
    pygame.midi.quit()
    pygame.quit()

if __name__ == "__main__":
    piano_gui()