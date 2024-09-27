const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const colorPalette = document.getElementById('colorPalette');
const playButton = document.getElementById('playButton');
const clearButton = document.getElementById('clearButton');
const saveButton = document.getElementById('saveButton');
const eraserButton = document.getElementById('eraserButton');

// Define colors and notes based on the provided mapping.
const colors = ['#FF0000', '#FFA500', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF', '#FF00FF']; // Corresponding to C (ド), D (レ), E (ミ), etc.
const notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']; // C corresponds to ド, D to レ, etc.
let selectedColor = colors[0];
let isEraserActive = false; // Flag to track eraser mode
const grid = Array(3).fill().map(() => Array(16).fill(null)); // Three rows grid with 16 columns each

// Create the color palette buttons.
colors.forEach((color) => {
    const button = document.createElement('button');
    button.className = 'color-button';
    button.style.backgroundColor = color;
    button.addEventListener('click', () => {
        selectedColor = color;
        isEraserActive = false; // Disable eraser mode when selecting a color
    });
    colorPalette.appendChild(button);
});

// Draw the staff lines with increased spacing and multiple staves.
function drawStaff() {
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 1;
    const staffSpacing = 20; // Vertical spacing between lines within a single staff
    const staffSetSpacing = 120; // Vertical spacing between each set of staves

    // Draw three sets of staves
    for (let set = 0; set < 3; set++) {
        const offset = set * staffSetSpacing; // Vertical offset for each set of staves
        for (let i = 0; i < 5; i++) {
            ctx.beginPath();
            ctx.moveTo(0, 40 + offset + i * staffSpacing);
            ctx.lineTo(canvas.width, 40 + offset + i * staffSpacing);
            ctx.stroke();
        }
    }
}

// Draw the color grid within the corresponding staff areas.
function drawGrid() {
    const cellWidth = canvas.width / 16;
    const cellHeight = 80; // Each cell spans the height between the first and last staff line in a set
    const staffTopOffsets = [40, 160, 280]; // Starting Y positions for each set of staves

    grid.forEach((row, y) => {
        row.forEach((cell, x) => {
            if (cell) {
                ctx.fillStyle = cell;
                ctx.fillRect(x * cellWidth, staffTopOffsets[y], cellWidth, cellHeight);
            }
        });
    });
}

// Handle canvas clicks to fill the tall grid cells with the selected color or erase.
canvas.addEventListener('click', (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / (canvas.width / 16));
    const y = Math.floor((event.clientY - rect.top - 40) / 120); // Adjust click detection to match the staff set height

    if (y >= 0 && y < 3) { // Ensure the click is within the grid range of the three rows
        if (isEraserActive) {
            grid[y][x] = null; // Clear the cell if eraser is active
        } else {
            grid[y][x] = selectedColor; // Fill the cell with the selected color
        }
        drawStaff();
        drawGrid();
    }
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
    drawGrid();
});
eraserButton.addEventListener('click', () => {
    isEraserActive = true; // Activate eraser mode
});
saveButton.addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'musical-color-grid.png';
    link.href = canvas.toDataURL();
    link.click();
});

// Initial drawing of the staff.
drawStaff();
drawGrid();
