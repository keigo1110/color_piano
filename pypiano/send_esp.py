'''アプリで選んだRGB値をESPに送信するコード'''
import requests
import json
import pygame
import mido
import sys

# ESP server URL with the correct endpoint
esp_url = "http://10.42.0.184:5000/ws"

# Function to send RGB color data to ESP
def send_color_to_esp(r, g, b):
    color_data = {
        "r": r,
        "g": g,
        "b": b
    }
    try:
        # Sending POST request to the ESP
        headers = {'Content-Type': 'application/json'}
        response = requests.post(esp_url, headers=headers, json=color_data)

        # Print the response from the server
        if response.status_code == 200:
            print("Successfully sent color data:", response.text)
        else:
            print(f"Failed to send color data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to ESP: {e}")

# Pygame initialization
pygame.init()

# Window settings
canvas_width = 1000
canvas_height = 240  # 3 rows with each row 80px
rows = 1
cols = 64
cell_width = canvas_width // cols
cell_height = 80

# Color and note mapping
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

# Drum-specific colors
drum_color_map = {
    "White": {"sample": "hat.wav", "color": (255, 255, 255)},
    "Black": {"sample": "kick.wav", "color": (1, 1, 1)}
}

# Load sound files (for drums)
pygame.mixer.init()
hat_sound = pygame.mixer.Sound('hat.wav')
kick_sound = pygame.mixer.Sound('kick.wav')

# Grid data
grid = [[None for _ in range(cols)] for _ in range(rows)]
selected_color = "Red"  # Default selected color
previous_selected_color = None  # To track the previously selected color
is_erasing = False

# MIDI initialization
outport = mido.open_output('IAC Driver My Port1')

# Window setup
screen = pygame.display.set_mode((canvas_width, canvas_height + 100))  # Extended height for palette
pygame.display.set_caption("Interactive Music Grid")

# Draw color palette
def draw_palette():
    palette_x = 20
    palette_y = canvas_height + 10
    button_size = 50

    for i, (key, value) in enumerate(color_note_map.items()):
        pygame.draw.rect(screen, value["color"], (palette_x + i * (button_size + 10), palette_y, button_size, button_size))

# Draw grid
def draw_grid():
    for row in range(rows):
        for col in range(cols):
            color = (255, 255, 255) if grid[row][col] is None else grid[row][col]["color"]
            pygame.draw.rect(screen, color, (col * cell_width, row * cell_height, cell_width, cell_height))
            pygame.draw.rect(screen, (0, 0, 0), (col * cell_width, row * cell_height, cell_width, cell_height), 1)

# Draw staves
def draw_staves():
    for row in range(2):  # Only the top 2 rows
        start_y = row * cell_height
        line_spacing = cell_height // 6
        for i in range(1, 6):
            y_pos = start_y + i * line_spacing
            pygame.draw.line(screen, (0, 0, 0), (0, y_pos), (canvas_width, y_pos), 1)

# Handle mouse click on grid
def handle_mouse_click(pos):
    col = pos[0] // cell_width
    row = pos[1] // cell_height

    # If click is out of grid bounds, do nothing
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

# Handle palette click
def handle_palette_click(pos):
    global previous_selected_color
    palette_x = 20
    palette_y = canvas_height + 10
    button_size = 50
    for i, key in enumerate(color_note_map.keys()):
        palette_rect = pygame.Rect(palette_x + i * (button_size + 10), palette_y, button_size, button_size)
        if palette_rect.collidepoint(pos):
            if key != previous_selected_color:
                previous_selected_color = key
                r, g, b = color_note_map[key]["color"]
                send_color_to_esp(r, g, b)  # Send RGB data when a new color is selected
            return key
    return None

# 列の再生
playing_notes = [None for _ in range(rows)]  # To store the currently playing note for each row

# Play column
def play_column(col):
    for row in range(rows):
        cell = grid[row][col]
        previous_cell = grid[row][col - 1] if col > 0 else None  # Check the previous column

        if cell:
            if row < 2:  # For musical notes
                midi_note = color_note_map[cell["key"]]["note"]

                # If this cell has the same note as the previous one, sustain the note
                if previous_cell and previous_cell == cell:
                    continue  # Do nothing, continue the sustain

                # If a new note starts, play it
                outport.send(mido.Message('note_on', note=midi_note, velocity=100))
                playing_notes[row] = midi_note  # Track the playing note for this row
            elif row == 2:  # For drum sounds
                if cell["key"] == "White":
                    hat_sound.play()
                elif cell["key"] == "Black":
                    kick_sound.play()
        else:
            # If there was a note playing in the previous column, stop it
            if playing_notes[row]:
                outport.send(mido.Message('note_off', note=playing_notes[row], velocity=100))
                playing_notes[row] = None  # Reset the playing note

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

    # If at the start, reset any sustained notes
    if column == 0:
        for row in range(rows):
            if playing_notes[row]:
                outport.send(mido.Message('note_off', note=playing_notes[row], velocity=100))
                playing_notes[row] = None  # Reset all playing notes

    play_column(column)

# Main loop
running = True
is_playing = False
clock = pygame.time.Clock()

# Playback interval and progress speed
play_interval = 2000  # 2000ms for one loop
last_time = pygame.time.get_ticks()

while running:
    screen.fill((255, 255, 255))
    draw_grid()
    draw_staves()
    draw_palette()  # Draw color palette

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[1] > canvas_height:  # Check if palette was clicked
                selected_color = handle_palette_click(event.pos)
            else:
                handle_mouse_click(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                clear_grid()
            elif event.key == pygame.K_SPACE:
                is_playing = not is_playing

    # Playback
    if is_playing:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - last_time

        # Smoothly progress playback bar position
        progress = (elapsed_time % play_interval) / play_interval
        draw_playback_bar(progress)

        # Play sounds
        play_sounds(progress)

        if elapsed_time >= play_interval:
            last_time = current_time

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()