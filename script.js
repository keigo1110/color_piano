const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const colorPalette = document.getElementById('colorPalette');
const clearButton = document.getElementById('clearButton');
const saveButton = document.getElementById('saveButton');
const eraserButton = document.getElementById('eraserButton');

// Define colors for each instrument.
const colors = ['#FF0000', '#FFA500', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF', '#FF00FF']; // Piano note colors
const notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']; // Corresponding piano notes
let selectedColor = colors[0];
let isEraserActive = false; // Flag to track eraser mode
const grid = Array(3).fill().map(() => Array(16).fill(null)); // Three rows grid with 16 columns each
let currentColumn = -1; // Track the current column being played
let isPlaying = false; // Flag to track playback status

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

// Draw the color grid within the corresponding staff areas and highlight the current column.
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

    // Draw the moving bar if a column is currently being played
    if (currentColumn >= 0) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)'; // Semi-transparent bar to indicate playback
        ctx.fillRect(currentColumn * cellWidth, 40, cellWidth, canvas.height - 40);
    }
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

// Frequencies for piano notes C4 to B4.
const pianoFrequencies = {
    'C': 261.63, // C4
    'D': 293.66, // D4
    'E': 329.63, // E4
    'F': 349.23, // F4
    'G': 392.00, // G4
    'A': 440.00, // A4
    'B': 493.88  // B4
};

// Bass and drum sounds configuration (mock frequencies and sounds).
const bassFrequencies = [110, 123.47, 146.83]; // Mock frequencies for bass sounds
const drumSounds = { 'white': 'hat', 'black': 'kick' }; // White for "チャ" (hat), black for "ドン" (kick)

// Play the notes associated with the grid colors and animate the moving bar.
function playNotes() {
    if (isPlaying) return; // Prevent starting a new playback while one is ongoing
    isPlaying = true;
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    let time = audioContext.currentTime;

    function loop() {
        const playTime = audioContext.currentTime;
        const columnDuration = 0.25; // 250ms per column

        grid[0].forEach((_, columnIndex) => {
            const scheduleTime = playTime + columnIndex * columnDuration;

            // Schedule the column change visually and sonically
            setTimeout(() => {
                currentColumn = columnIndex;
                drawStaff();
                drawGrid();
                playColumnNotes(audioContext, columnIndex, scheduleTime);
                if (columnIndex === 15) {
                    setTimeout(() => {
                        currentColumn = -1;
                        drawStaff();
                        drawGrid();
                        loop(); // Restart the loop for continuous playback
                    }, columnDuration * 1000);
                }
            }, columnIndex * columnDuration * 1000);
        });
    }

    loop(); // Start the loop
}

// Play notes for a specific column based on the instrument set with envelopes.
function playColumnNotes(audioContext, columnIndex, time) {
    const attackTime = 0.1;
    const releaseTime = 0.2;

    grid.forEach((row, rowIndex) => {
        const cell = row[columnIndex];
        if (cell) {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            // Envelope setup
            gainNode.gain.setValueAtTime(0, time);
            gainNode.gain.linearRampToValueAtTime(1, time + attackTime); // Attack
            gainNode.gain.setValueAtTime(1, time + attackTime + 0.2); // Sustain
            gainNode.gain.linearRampToValueAtTime(0, time + attackTime + releaseTime); // Release

            if (rowIndex === 0) { // Top row for piano
                const noteIndex = colors.indexOf(cell);
                if (noteIndex !== -1) {
                    const frequency = pianoFrequencies[notes[noteIndex]];
                    oscillator.frequency.setValueAtTime(frequency, time);
                }
            } else if (rowIndex === 1) { // Middle row for bass
                const bassIndex = Math.floor(Math.random() * bassFrequencies.length);
                oscillator.frequency.setValueAtTime(bassFrequencies[bassIndex], time);
            } else if (rowIndex === 2) { // Bottom row for drums
                playDrumSound(cell === '#FFFFFF' ? drumSounds['white'] : drumSounds['black']);
            }

            oscillator.start(time);
            oscillator.stop(time + attackTime + releaseTime);
        }
    });
}

// Function to simulate drum sounds based on the color (white for "チャ", black for "ドン").
function playDrumSound(soundType) {
    console.log(`Playing drum sound: ${soundType}`);
}

// Event listeners for the buttons.
clearButton.addEventListener('click', () => {
    grid.forEach(row => row.fill(null));
    currentColumn = -1; // Reset current column
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

// Initial drawing of the staff and start playback automatically.
drawStaff();
drawGrid();
playNotes();
