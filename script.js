const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const colorPalette = document.getElementById('colorPalette');
const playButton = document.getElementById('playButton');
const clearButton = document.getElementById('clearButton');
const saveButton = document.getElementById('saveButton');

// Define colors and notes based on the provided mapping.
const colors = ['#FF0000', '#FFA500', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF', '#FF00FF']; // Corresponding to C (ド), D (レ), E (ミ), etc.
const notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']; // C corresponds to ド, D to レ, etc.
let selectedColor = colors[0];
const grid = Array(4).fill().map(() => Array(16).fill(null));

// Create the color palette buttons.
colors.forEach((color) => {
    const button = document.createElement('button');
    button.className = 'color-button';
    button.style.backgroundColor = color;
    button.addEventListener('click', () => selectedColor = color);
    colorPalette.appendChild(button);
});

// Draw the staff lines.
function drawStaff() {
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 1;
    for (let i = 0; i < 5; i++) {
        ctx.beginPath();
        ctx.moveTo(0, 40 + i * 15);
        ctx.lineTo(canvas.width, 40 + i * 15);
        ctx.stroke();
    }
}

// Draw the color grid on the staff.
function drawGrid() {
    const cellWidth = canvas.width / 16;
    const cellHeight = canvas.height / 4;
    grid.forEach((row, y) => {
        row.forEach((cell, x) => {
            if (cell) {
                ctx.fillStyle = cell;
                ctx.fillRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
            }
        });
    });
}

// Handle canvas clicks to fill grid with the selected color.
canvas.addEventListener('click', (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / (canvas.width / 16));
    const y = Math.floor((event.clientY - rect.top) / (canvas.height / 4));
    grid[y][x] = selectedColor;
    drawStaff();
    drawGrid();
});

// Frequencies for C4 to B4 based on the specified website.
const frequencies = {
    'C': 261.63, // C4
    'D': 293.66, // D4
    'E': 329.63, // E4
    'F': 349.23, // F4
    'G': 392.00, // G4
    'A': 440.00, // A4
    'B': 493.88  // B4
};

// Play the notes associated with the grid colors.
function playNotes() {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    let time = audioContext.currentTime;
    grid.forEach(row => {
        row.forEach(cell => {
            if (cell) {
                const oscillator = audioContext.createOscillator();
                oscillator.type = 'sine';
                const noteIndex = colors.indexOf(cell);
                if (noteIndex !== -1) {
                    const frequency = frequencies[notes[noteIndex]]; // Use exact frequency for each note.
                    oscillator.frequency.setValueAtTime(frequency, time);
                    oscillator.connect(audioContext.destination);
                    oscillator.start(time);
                    oscillator.stop(time + 0.2);
                    time += 0.25; // Quarter note duration
                }
            } else {
                time += 0.25; // Maintain timing even if no note is played
            }
        });
    });
}

// Event listeners for the buttons.
playButton.addEventListener('click', playNotes);
clearButton.addEventListener('click', () => {
    grid.forEach(row => row.fill(null));
    drawStaff();
});
saveButton.addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'musical-color-grid.png';
    link.href = canvas.toDataURL();
    link.click();
});

// Initial drawing of the staff.
drawStaff();
