from flask import Flask, jsonify, request, render_template
import mido
import pygame

# PygameとMIDIの初期化
pygame.mixer.init()
outport = mido.open_output('IAC Driver My Port1')
hat_sound = pygame.mixer.Sound('static/audio/hat.wav')
kick_sound = pygame.mixer.Sound('static/audio/kick.wav')

app = Flask(__name__)

# 色と音のマッピング
color_note_map = {
    "Red": {"note": 60},  # C4
    "Orange-pink": {"note": 67},  # G4
    "Yellow": {"note": 62},  # D4
    "Green": {"note": 69},  # A4
    "Whitish-blue": {"note": 64},  # E4
    "Blue, bright": {"note": 66},  # F#4
    "Violet": {"note": 61},  # Db4
    "Purplish-violet": {"note": 68},  # Ab4
    "Steel color with metallic sheen": {"note": 65},  # Eb4
    "Red, dark": {"note": 63}  # F4
}

# ドラム専用の色
drum_color_map = {
    "White": "hat.wav",
    "Black": "kick.wav"
}

# フロントエンドのHTMLを提供
@app.route('/')
def index():
    return render_template('index.html')

# ノートの再生
@app.route('/play_note', methods=['POST'])
def play_note():
    data = request.json
    color = data.get('color')
    note_type = data.get('type')

    if note_type == 'note' and color in color_note_map:
        midi_note = color_note_map[color]["note"]
        outport.send(mido.Message('note_on', note=midi_note, velocity=100))
        return jsonify({"status": "note played", "note": midi_note})
    elif note_type == 'drum' and color in drum_color_map:
        sound_file = drum_color_map[color]
        if sound_file == "hat.wav":
            hat_sound.play()
        elif sound_file == "kick.wav":
            kick_sound.play()
        return jsonify({"status": "drum sound played", "sound": sound_file})

    return jsonify({"status": "error", "message": "Invalid input"})

if __name__ == '__main__':
    app.run(debug=True)
