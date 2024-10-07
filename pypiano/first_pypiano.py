'''jsのシステムをpygameでつくる'''
import pygame
import mido
import sys

# Pygameの初期化
pygame.init()

# ウィンドウの設定
canvas_width = 1000
canvas_height = 240  # 3行で1行80px
rows = 1
cols = 64
cell_width = canvas_width // cols
cell_height = 80

# 色と音のマッピング
color_note_map = {
    "Red": {"note": 60, "color": (255, 0, 0)},  # C4
    "Orange-pink": {"note": 67, "color": (255, 153, 102)},  # G4 (#FF9966)
    "Yellow": {"note": 62, "color": (255, 255, 0)},  # D4
    "Green": {"note": 69, "color": (0, 255, 0)},  # A4
    "Whitish-blue": {"note": 64, "color": (224, 255, 255)},  # E4 (#E0FFFF)
    "Blue, bright": {"note": 66, "color": (0, 0, 255)},  # F#4
    "Violet": {"note": 61, "color": (238, 130, 238)},  # Db4
    "Purplish-violet": {"note": 68, "color": (75, 0, 130)},  # Ab4 (Indigo)
    "Steel color with metallic sheen": {"note": 65, "color": (70, 130, 180)},  # Eb4 (Steel Blue)
    "Red, dark": {"note": 63, "color": (139, 0, 0)}  # F4
}

# ドラム専用の色
drum_color_map = {
    "White": {"sample": "hat.wav", "color": (255, 255, 255)},
    "Black": {"sample": "kick.wav", "color": (1, 1, 1)}
}

# サウンドファイルの読み込み（ドラム用）
pygame.mixer.init()
hat_sound = pygame.mixer.Sound('hat.wav')
kick_sound = pygame.mixer.Sound('kick.wav')

# グリッドのデータ
grid = [[None for _ in range(cols)] for _ in range(rows)]
selected_color = "Red"  # デフォルトの選択色
is_erasing = False

# MIDIの初期化
outport = mido.open_output('IAC Driver My Port1')

# ウィンドウの設定
screen = pygame.display.set_mode((canvas_width, canvas_height + 100))  # パレット用に高さを拡張
pygame.display.set_caption("Interactive Music Grid")

# カラーパレット描画
def draw_palette():
    palette_x = 20
    palette_y = canvas_height + 10
    button_size = 50

    for i, (key, value) in enumerate(color_note_map.items()):
        pygame.draw.rect(screen, value["color"], (palette_x + i * (button_size + 10), palette_y, button_size, button_size))

# グリッドの描画
def draw_grid():
    for row in range(rows):
        for col in range(cols):
            color = (255, 255, 255) if grid[row][col] is None else grid[row][col]["color"]
            pygame.draw.rect(screen, color, (col * cell_width, row * cell_height, cell_width, cell_height))
            pygame.draw.rect(screen, (0, 0, 0), (col * cell_width, row * cell_height, cell_width, cell_height), 1)

# 五線譜の描画
def draw_staves():
    for row in range(2):  # 上2行のみ
        start_y = row * cell_height
        line_spacing = cell_height // 6
        for i in range(1, 6):
            y_pos = start_y + i * line_spacing
            pygame.draw.line(screen, (0, 0, 0), (0, y_pos), (canvas_width, y_pos), 1)

# セルをクリックしたときの処理
def handle_mouse_click(pos):
    col = pos[0] // cell_width
    row = pos[1] // cell_height

    # グリッドの範囲外なら処理をしない
    if row >= rows or col >= cols:
        return

    if row < rows:
        if is_erasing:
            grid[row][col] = None
        else:
            if row < 2 and selected_color in color_note_map:
                grid[row][col] = {"key": selected_color, "color": color_note_map[selected_color]["color"]}
            elif row == 2 and selected_color in drum_color_map:
                grid[row][col] = {"key": selected_color, "color": drum_color_map[selected_color]["color"]}

# カラーパレットのクリック処理
def handle_palette_click(pos):
    palette_x = 20
    palette_y = canvas_height + 10
    button_size = 50
    for i, key in enumerate(color_note_map.keys()):
        palette_rect = pygame.Rect(palette_x + i * (button_size + 10), palette_y, button_size, button_size)
        if palette_rect.collidepoint(pos):
            return key
    return None

# 列の再生
def play_column(col):
    for row in range(rows):
        cell = grid[row][col]
        if cell:
            if row < 2:
                midi_note = color_note_map[cell["key"]]["note"]
                outport.send(mido.Message('note_on', note=midi_note, velocity=100))
                pygame.time.wait(1)  # 音を鳴らす時間を少し待つ
                outport.send(mido.Message('note_off', note=midi_note, velocity=100))
            elif row == 2:
                if cell["key"] == "White":
                    hat_sound.play()
                elif cell["key"] == "Black":
                    kick_sound.play()

# 再生バーの描画
def draw_playback_bar(position):
    bar_color = (255, 255, 0, 128)  # 半透明の黄色
    pygame.draw.rect(screen, bar_color, (position * canvas_width, 0, cell_width, canvas_height))

# グリッドのリセット
def clear_grid():
    global grid
    grid = [[None for _ in range(cols)] for _ in range(rows)]

# 音の再生処理
def play_sounds(progress):
    column = int(progress * cols)
    play_column(column)

# メインループ
running = True
is_playing = False
clock = pygame.time.Clock()

# 再生間隔と進行スピードの調整
play_interval = 2000  # 2000msで1周
last_time = pygame.time.get_ticks()

while running:
    screen.fill((255, 255, 255))
    draw_grid()
    draw_staves()
    draw_palette()  # カラーパレットの描画

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[1] > canvas_height:  # カラーパレットがクリックされたか確認
                selected_color = handle_palette_click(event.pos)
            else:
                handle_mouse_click(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                clear_grid()
            elif event.key == pygame.K_SPACE:
                is_playing = not is_playing

    # 再生中の処理
    if is_playing:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - last_time

        # 再生バーの位置を滑らかに進行
        progress = (elapsed_time % play_interval) / play_interval
        draw_playback_bar(progress)

        # 音を再生
        play_sounds(progress)

        if elapsed_time >= play_interval:
            last_time = current_time

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
