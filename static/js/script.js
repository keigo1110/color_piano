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
    "Red": "C4",
    "Orange-pink": "G4",
    "Yellow": "D4",
    "Green": "A4",
    "Whitish-blue": "E4",
    "Blue, bright": "F#4",
    "Violet": "Db4",
    "Purplish-violet": "Ab4",
    "Steel color with metallic sheen": "Eb4",
    "Red, dark": "F4"
};

const colors = Object.keys(colorNoteMap);
let selectedColor = colors[0]; // デフォルトの選択色
let eraserMode = false; // 消しゴムモード

// コントロール要素
const paletteDiv = document.getElementById('palette');
const eraserButton = document.getElementById('eraserButton');
const clearButton = document.getElementById('clearButton');
const saveButton = document.getElementById('saveButton');
const playButton = document.getElementById('playButton');

// カラーパレットの生成
colors.forEach(color => {
    const colorBtn = document.createElement('button');
    colorBtn.className = 'color-button';
    colorBtn.style.backgroundColor = color;
    colorBtn.addEventListener('click', () => {
        selectedColor = color;
        eraserMode = false;
    });
    paletteDiv.appendChild(colorBtn);
});

// コントロールボタンのイベント
eraserButton.addEventListener('click', () => {
    eraserMode = true;
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
        grid[y][x] = selectedColor;
    }
    drawGrid();
});

// グリッドの描画
function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // セルの描画
    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            const color = grid[y][x];
            if (color) {
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
    for (let y = 0; y < rows; y++) {
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
            const color = grid[y][currentColumn];
            if (color) {
                playSound(y, color);
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
function playSound(row, color) {
    if (row === 0) {
        // ピアノシンセ
        const synth = new Tone.Synth().toDestination();
        synth.triggerAttackRelease(colorNoteMap[color], '8n');
    } else if (row === 1) {
        // ベースシンセ
        const bassSynth = new Tone.MembraneSynth().toDestination();
        bassSynth.triggerAttackRelease(colorNoteMap[color], '8n');
    } else if (row === 2) {
        // ドラムサンプル
        const player = new Tone.Player().toDestination();
        if (color === 'Whitish-blue') {
            player.load('/static/audio/hat.wav').then(() => {
                player.start();
            });
        } else {
            player.load('/static/audio/kick.wav').then(() => {
                player.start();
            });
        }
    }
}

// 初期描画
drawGrid();
