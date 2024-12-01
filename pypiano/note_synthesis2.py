import pygame
import mido
import sys

# Pygameの初期化
pygame.init()

# ウィンドウの設定（フレキシブルに対応）
canvas_width = 1000
canvas_height = 240  # 3行で1行80px
rows = 1
cols = 64

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
screen = pygame.display.set_mode((canvas_width, canvas_height + 100), pygame.RESIZABLE)  # ウィンドウをリサイズ可能に
pygame.display.set_caption("Interactive Music Grid")

# グリッドの描画関数
def draw_grid(cell_width, cell_height):
    for row in range(rows):
        for col in range(cols):
            color = (255, 255, 255) if grid[row][col] is None else grid[row][col]["color"]
            pygame.draw.rect(screen, color, (col * cell_width, row * cell_height, cell_width, cell_height))
            pygame.draw.rect(screen, (0, 0, 0), (col * cell_width, row * cell_height, cell_width, cell_height), 1)

# ウィンドウのリサイズに対応してグリッドサイズを動的に調整
def handle_window_resize(event):
    global canvas_width, canvas_height, cols, rows
    canvas_width, canvas_height = event.w, event.h - 100
    cell_width = canvas_width // cols
    cell_height = canvas_height // rows
    return cell_width, cell_height

# セルをクリックしたときの処理
def handle_mouse_click(pos, cell_width, cell_height):
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

# メインループ
running = True
is_playing = False
clock = pygame.time.Clock()
play_interval = 2000  # 2000msで1周
last_time = pygame.time.get_ticks()

while running:
    screen.fill((255, 255, 255))
    cell_width = canvas_width // cols
    cell_height = canvas_height // rows

    draw_grid(cell_width, cell_height)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            cell_width, cell_height = handle_window_resize(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[1] > canvas_height:  # カラーパレットがクリックされたか確認
                selected_color = handle_palette_click(event.pos)
            else:
                handle_mouse_click(pygame.mouse.get_pos(), cell_width, cell_height)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                clear_grid()
            elif event.key == pygame.K_SPACE:
                is_playing = not is_playing

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
