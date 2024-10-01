// キャンバス設定
const canvas = document.getElementById('gridCanvas');
const ctx = canvas.getContext('2d');

// グリッド設定
const rows = 3;
const cols = 8;
const cellWidth = canvas.width / cols;
const cellHeight = 80; // 固定のセル高さ

// グリッドデータの初期化
let grid = Array(rows).fill().map(() => Array(cols).fill(null));

// カラーパレットと音のリスト
const colorNoteMap = {
    "Red": { note: "C4", color: "red" },
    "Orange-pink": { note: "G4", color: "#FF9966" },
    "Yellow": { note: "D4", color: "yellow" },
    "Green": { note: "A4", color: "green" },
    "Whitish-blue": { note: "E4", color: "#E0FFFF" }, // Light Cyan
    "Blue, bright": { note: "F#4", color: "blue" },
    "Violet": { note: "Db4", color: "violet" },
    "Purplish-violet": { note: "Ab4", color: "indigo" },
    "Steel color with metallic sheen": { note: "Eb4", color: "#4682B4" }, // Steel Blue
    "Red, dark": { note: "F4", color: "darkred" }
};

const drumColorMap = {
    "White": { sample: "hat", color: "white" },
    "Black": { sample: "kick", color: "black" }
};

const mainColors = Object.keys(colorNoteMap);
const drumColors = Object.keys(drumColorMap);

let selectedColor = null; // 選択された色（キー）
let selectedPalette = null; // 選択されたパレット（"main" または "drum"）
let eraserMode = false; // 消しゴムモード

// コントロール要素
const mainPaletteDiv = document.getElementById('mainPalette');
const drumPaletteDiv = document.getElementById('drumPalette');
const eraserButton = document.getElementById('eraserButton');
const clearButton = document.getElementById('clearButton');
const saveButton = document.getElementById('saveButton');
const playButton = document.getElementById('playButton');

// メインパレットの生成
mainColors.forEach(key => {
    const colorInfo = colorNoteMap[key];
    const colorBtn = document.createElement('button');
    colorBtn.className = 'color-button';
    colorBtn.style.backgroundColor = colorInfo.color;
    colorBtn.addEventListener('click', () => {
        selectedColor = key;
        selectedPalette = "main";
        eraserMode = false;
    });
    mainPaletteDiv.appendChild(colorBtn);
});

// ドラムパレットの生成
drumColors.forEach(key => {
    const colorInfo = drumColorMap[key];
    const colorBtn = document.createElement('button');
    colorBtn.className = 'drum-button';
    colorBtn.style.backgroundColor = colorInfo.color;
    colorBtn.addEventListener('click', () => {
        selectedColor = key;
        selectedPalette = "drum";
        eraserMode = false;
    });
    drumPaletteDiv.appendChild(colorBtn);
});

// コントロールボタンのイベント
eraserButton.addEventListener('click', () => {
    eraserMode = true;
    selectedColor = null;
    selectedPalette = null;
});

clearButton.addEventListener('click', () => {
    grid = Array(rows).fill().map(() => Array(cols).fill(null));
    drawGrid();
});

saveButton.addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'grid.png';
    link.href = canvas.toDataURL();
    link.click();
});

let isPlaying = false;
playButton.addEventListener('click', () => {
    isPlaying = !isPlaying;
    if (isPlaying) {
        playButton.textContent = '停止';
        startPlayback();
    } else {
        playButton.textContent = '再生';
        stopPlayback();
    }
});

// キャンバスのクリックイベント
canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / cellWidth);
    const y = Math.floor((e.clientY - rect.top) / cellHeight);

    if (eraserMode) {
        grid[y][x] = null;
    } else {
        if (y < 2 && selectedPalette === "main") {
            // 最初の2行はメインパレットのみ
            grid[y][x] = { key: selectedColor, palette: selectedPalette };
        } else if (y === 2 && selectedPalette === "drum") {
            // 第3行はドラムパレットのみ
            grid[y][x] = { key: selectedColor, palette: selectedPalette };
        }
        // 適切なパレットが選択されていない場合は何もしない
    }
    drawGrid();
});

// グリッドの描画
function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // セルの描画
    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            const cell = grid[y][x];
            if (cell) {
                let color;
                if (cell.palette === "main") {
                    color = colorNoteMap[cell.key].color;
                } else if (cell.palette === "drum") {
                    color = drumColorMap[cell.key].color;
                }
                ctx.fillStyle = color;
                ctx.fillRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
            }
            ctx.strokeStyle = '#000';
            ctx.strokeRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
        }
    }

    // 五線譜の描画
    drawStaves();
}

// 五線譜の描画
function drawStaves() {
    ctx.strokeStyle = '#000';
    for (let y = 0; y < 2; y++) { // 最初の2行のみ
        const startY = y * cellHeight;
        const lineSpacing = cellHeight / 6;
        for (let i = 1; i <= 5; i++) {
            const yPos = startY + i * lineSpacing;
            ctx.beginPath();
            ctx.moveTo(0, yPos);
            ctx.lineTo(canvas.width, yPos);
            ctx.stroke();
        }
    }
}

// 再生ロジック
let currentColumn = 0;
let playbackInterval;

function startPlayback() {
    playbackInterval = setInterval(() => {
        // 現在の列をハイライト
        drawGrid();
        ctx.fillStyle = 'rgba(255, 255, 0, 0.3)';
        ctx.fillRect(currentColumn * cellWidth, 0, cellWidth, canvas.height);

        // 音の再生
        for (let y = 0; y < rows; y++) {
            const cell = grid[y][currentColumn];
            if (cell) {
                playSound(y, cell.key, cell.palette);
            }
        }

        currentColumn = (currentColumn + 1) % cols;
    }, 600); // 600ミリ秒ごとに移動
}

function stopPlayback() {
    clearInterval(playbackInterval);
    currentColumn = 0;
    drawGrid();
}

// 音の再生
function playSound(row, key, palette) {
    if (palette === "main") {
        const note = colorNoteMap[key].note;
        if (row === 0) {
            // ピアノシンセ
            const synth = new Tone.Synth().toDestination();
            synth.triggerAttackRelease(note, '8n');
        } else if (row === 1) {
            // ベースシンセ
            const bassSynth = new Tone.MembraneSynth().toDestination();
            bassSynth.triggerAttackRelease(note, '8n');
        }
    } else if (palette === "drum" && row === 2) {
        // ドラムサンプル
        const sampleName = drumColorMap[key].sample;
        const player = new Tone.Player(`/static/audio/${sampleName}.wav`).toDestination();
        player.autostart = true;
    }
}

// 初期描画
drawGrid();
