// --- Level Definitions (20 puzzles) ---
const levels = [
  // Level 1
  { gridSize: 5, placements: [
      { x: 1, y: 2, type: 'resistor' },
      { x: 2, y: 2, type: 'capacitor' },
      { x: 3, y: 2, type: 'switch' }
  ]},
  // Level 2
  { gridSize: 6, placements: [
      { x: 1, y: 1, type: 'capacitor' },
      { x: 4, y: 2, type: 'resistor' },
      { x: 2, y: 4, type: 'switch' },
      { x: 3, y: 4, type: 'resistor' }
  ]},
  // Level 3
  { gridSize: 7, placements: [
      { x: 2, y: 2, type: 'resistor' },
      { x: 3, y: 3, type: 'capacitor' },
      { x: 4, y: 4, type: 'switch' },
      { x: 5, y: 5, type: 'resistor' }
  ]},
  // Level 4
  { gridSize: 7, placements: [
      { x: 1, y: 7, type: 'switch' },
      { x: 2, y: 5, type: 'capacitor' },
      { x: 4, y: 2, type: 'resistor' },
      { x: 6, y: 4, type: 'switch' },
      { x: 7, y: 7, type: 'capacitor' }
  ]},
  // Level 5
  { gridSize: 8, placements: [
      { x: 3, y: 2, type: 'resistor' },
      { x: 3, y: 3, type: 'capacitor' },
      { x: 3, y: 4, type: 'switch' },
      { x: 5, y: 6, type: 'resistor' },
      { x: 6, y: 6, type: 'capacitor' }
  ]},
  // Level 6
  { gridSize: 8, placements: [
      { x: 2, y: 7, type: 'switch' },
      { x: 4, y: 5, type: 'resistor' },
      { x: 5, y: 4, type: 'capacitor' },
      { x: 6, y: 3, type: 'switch' },
      { x: 8, y: 8, type: 'resistor' }
  ]},
  // Level 7
  { gridSize: 9, placements: [
      { x: 1, y: 1, type: 'capacitor' },
      { x: 3, y: 3, type: 'resistor' },
      { x: 5, y: 5, type: 'switch' },
      { x: 7, y: 7, type: 'capacitor' },
      { x: 9, y: 9, type: 'resistor' },
      { x: 2, y: 9, type: 'switch' }
  ]},
  // Level 8
  { gridSize: 9, placements: [
      { x: 4, y: 2, type: 'resistor' },
      { x: 4, y: 3, type: 'capacitor' },
      { x: 4, y: 4, type: 'switch' },
      { x: 6, y: 6, type: 'resistor' },
      { x: 7, y: 6, type: 'capacitor' },
      { x: 8, y: 6, type: 'switch' }
  ]},
  // Level 9
  { gridSize: 10, placements: [
      { x: 2, y: 2, type: 'resistor' },
      { x: 3, y: 2, type: 'capacitor' },
      { x: 4, y: 2, type: 'switch' },
      { x: 6, y: 8, type: 'resistor' },
      { x: 7, y: 8, type: 'capacitor' },
      { x: 8, y: 8, type: 'switch' }
  ]},
  // Level 10
  { gridSize: 10, placements: [
      { x: 1, y: 10, type: 'switch' },
      { x: 2, y: 8, type: 'resistor' },
      { x: 3, y: 6, type: 'capacitor' },
      { x: 5, y: 5, type: 'resistor' },
      { x: 7, y: 4, type: 'switch' },
      { x: 9, y: 2, type: 'capacitor' }
  ]},
  // Level 11
  { gridSize: 11, placements: [
      { x: 3, y: 3, type: 'resistor' },
      { x: 4, y: 4, type: 'capacitor' },
      { x: 5, y: 5, type: 'switch' },
      { x: 6, y: 6, type: 'resistor' },
      { x: 7, y: 7, type: 'capacitor' },
      { x: 8, y: 8, type: 'switch' }
  ]},
  // Level 12
  { gridSize: 11, placements: [
      { x: 2, y: 9, type: 'switch' },
      { x: 4, y: 7, type: 'resistor' },
      { x: 6, y: 5, type: 'capacitor' },
      { x: 8, y: 3, type: 'resistor' },
      { x: 10, y: 1, type: 'switch' },
      { x: 11, y: 11, type: 'capacitor' }
  ]},
  // Level 13
  { gridSize: 12, placements: [
      { x: 1, y: 6, type: 'capacitor' },
      { x: 3, y: 6, type: 'resistor' },
      { x: 5, y: 6, type: 'switch' },
      { x: 7, y: 6, type: 'capacitor' },
      { x: 9, y: 6, type: 'resistor' },
      { x: 11, y: 6, type: 'switch' }
  ]},
  // Level 14
  { gridSize: 12, placements: [
      { x: 2, y: 2, type: 'switch' },
      { x: 4, y: 4, type: 'resistor' },
      { x: 6, y: 6, type: 'capacitor' },
      { x: 8, y: 8, type: 'resistor' },
      { x: 10, y: 10, type: 'switch' },
      { x: 12, y: 12, type: 'capacitor' }
  ]},
  // Level 15
  { gridSize: 12, placements: [
      { x: 3, y: 11, type: 'resistor' },
      { x: 5, y: 9, type: 'capacitor' },
      { x: 7, y: 7, type: 'switch' },
      { x: 9, y: 5, type: 'resistor' },
      { x: 11, y: 3, type: 'capacitor' },
      { x: 12, y: 1, type: 'switch' }
  ]},
  // Level 16
  { gridSize: 12, placements: [
      { x: 1, y: 12, type: 'capacitor' },
      { x: 2, y: 10, type: 'resistor' },
      { x: 3, y: 8, type: 'switch' },
      { x: 4, y: 6, type: 'capacitor' },
      { x: 5, y: 4, type: 'resistor' },
      { x: 6, y: 2, type: 'switch' }
  ]},
  // Level 17
  { gridSize: 12, placements: [
      { x: 7, y: 1, type: 'switch' },
      { x: 8, y: 3, type: 'capacitor' },
      { x: 9, y: 5, type: 'resistor' },
      { x: 10, y: 7, type: 'switch' },
      { x: 11, y: 9, type: 'capacitor' },
      { x: 12, y: 11, type: 'resistor' }
  ]},
  // Level 18
  { gridSize: 12, placements: [
      { x: 6, y: 1, type: 'resistor' },
      { x: 6, y: 3, type: 'capacitor' },
      { x: 6, y: 5, type: 'switch' },
      { x: 6, y: 7, type: 'resistor' },
      { x: 6, y: 9, type: 'capacitor' },
      { x: 6, y: 11, type: 'switch' }
  ]},
  // Level 19
  { gridSize: 12, placements: [
      { x: 1, y: 1, type: 'switch' },
      { x: 3, y: 2, type: 'resistor' },
      { x: 5, y: 3, type: 'capacitor' },
      { x: 7, y: 4, type: 'switch' },
      { x: 9, y: 5, type: 'resistor' },
      { x: 11, y: 6, type: 'capacitor' }
  ]},
  // Level 20
  { gridSize: 12, placements: [
      { x: 2, y: 12, type: 'capacitor' },
      { x: 4, y: 11, type: 'resistor' },
      { x: 6, y: 10, type: 'switch' },
      { x: 8, y: 9, type: 'capacitor' },
      { x: 10, y: 8, type: 'resistor' },
      { x: 12, y: 7, type: 'switch' }
  ]}
];

// main.js

// State variables
let currentLevelIndex = 0;
let elapsedTime = 0;
let timerInterval = null;
let totalScore = 0;

// DOM references
const levelDisplay = document.getElementById('level-display');
const timerDisplay = document.getElementById('timer');
const scoreDisplay = document.getElementById('score');
const submitBtn = document.getElementById('submit-btn');
const palette = document.getElementById('palette');
const gridContainer = document.getElementById('grid-container');

// Initialize the first level
initLevel(currentLevelIndex);

function initLevel(index) {
  // Reset timer
  clearInterval(timerInterval);
  elapsedTime = 0;
  timerDisplay.textContent = `${elapsedTime}s`;

  // Update displays
  levelDisplay.textContent = index + 1;
  scoreDisplay.textContent = totalScore;

  // Build the grid
  buildGrid(levels[index].gridSize);

  // Set up drag-and-drop handlers
  setupDragAndDrop();

  // Start the timer
  timerInterval = setInterval(() => {
    elapsedTime++;
    timerDisplay.textContent = `${elapsedTime}s`;
  }, 1000);
}

function buildGrid(size) {
  // Clear previous cells
  gridContainer.innerHTML = '';
  // Apply CSS grid columns dynamically
  gridContainer.style.gridTemplateColumns = `repeat(${size}, 40px)`;

  // Create cells
  for (let y = 1; y <= size; y++) {
    for (let x = 1; x <= size; x++) {
      const cell = document.createElement('div');
      cell.classList.add('grid-cell');
      cell.dataset.x = x;
      cell.dataset.y = y;
      gridContainer.appendChild(cell);
    }
  }
}

function setupDragAndDrop() {
  // Palette items: dragstart
  document.querySelectorAll('#palette .component').forEach(comp => {
    comp.addEventListener('dragstart', e => {
      e.dataTransfer.setData('text/plain', comp.dataset.type);
    });
  });

  // Grid cells: dragover, dragleave, drop
  document.querySelectorAll('.grid-cell').forEach(cell => {
    cell.addEventListener('dragover', e => {
      e.preventDefault();
      cell.classList.add('highlight');
    });
    cell.addEventListener('dragleave', () => {
      cell.classList.remove('highlight');
    });
    cell.addEventListener('drop', e => {
      e.preventDefault();
      cell.classList.remove('highlight');
      const type = e.dataTransfer.getData('text/plain');
      placeComponent(cell, type);
    });
  });
}

function placeComponent(cell, type) {
  // Remove existing component
  const existing = cell.querySelector('.component');
  if (existing) existing.remove();

  // Create a new component element inside the cell
  const comp = document.createElement('div');
  comp.classList.add('component');
  comp.textContent = type.charAt(0).toUpperCase() + type.slice(1);
  comp.dataset.type = type;
  comp.setAttribute('draggable', 'false');

  cell.appendChild(comp);
}

// Submission handler: validate current placements
submitBtn.addEventListener('click', () => {
  const levelData = levels[currentLevelIndex];
  let correct = true;

  levelData.placements.forEach(({ x, y, type }) => {
    const selector = `.grid-cell[data-x="${x}"][data-y="${y}"] .component`;
    const placed = document.querySelector(selector);
    if (!placed || placed.dataset.type !== type) {
      correct = false;
    }
  });

  if (correct) {
    alert('Correct!');
    // TODO: compute score for this level, advance to next or finish
  } else {
    alert('Some placements are incorrect.');
  }
});


/* index.html addition, just before closing </body> */


// main.js additions

/**
 * Compute level score: base minus time penalty, with a floor.
 * @param {number} timeSec
 * @returns {number}
 */
function computeScore(timeSec) {
  const base = 1000;
  const penalty = timeSec * 10;
  return Math.max(base - penalty, 100);
}

/**
 * Called when a level is solved correctly
 */
function handleLevelCompletion() {
  clearInterval(timerInterval);
  const levelTime = elapsedTime;
  const levelScore = computeScore(levelTime);
  totalScore += levelScore;
  alert(`Level ${currentLevelIndex + 1} complete! You scored ${levelScore} points.`);
  scoreDisplay.textContent = totalScore;

  if (currentLevelIndex < levels.length - 1) {
    currentLevelIndex++;
    initLevel(currentLevelIndex);
  } else {
    showEndGame();
  }
}

/**
 * Display final overlay and hook restart
 */
function showEndGame() {
  const overlay = document.getElementById('endgame-overlay');
  document.getElementById('final-score').textContent = totalScore;
  overlay.style.display = 'flex';

  document.getElementById('restart-btn').addEventListener('click', () => {
    overlay.style.display = 'none';
    currentLevelIndex = 0;
    totalScore = 0;
    initLevel(0);
  });
}

// Update existing submit handler
submitBtn.addEventListener('click', () => {
  const levelData = levels[currentLevelIndex];
  let correct = true;

  // Check each required placement
  levelData.placements.forEach(({ x, y, type }) => {
    const cellComp = document.querySelector(
      `.grid-cell[data-x="${x}"][data-y="${y}"] .component`
    );
    if (!cellComp || cellComp.dataset.type !== type) {
      correct = false;
    }
  });

  if (correct) {
    handleLevelCompletion();
  } else {
    alert('Some placements are incorrect. Keep trying!');
  }
});
/* index.html: add Reset Level button */

// main.js: hook up reset and allow right-click removal
const resetBtn = document.getElementById('reset-btn');
resetBtn.addEventListener('click', () => {
  if (confirm('Reset level? All placements will be lost.')) {
    initLevel(currentLevelIndex);
  }
});

// In setupDragAndDrop(), after existing listeners for drag/drop:
function setupDragAndDrop() {
  document.querySelectorAll('#palette .component').forEach(comp => {
    // existing dragstart handler...
  });

  document.querySelectorAll('.grid-cell').forEach(cell => {
    // existing dragover, dragleave, drop handlers...

    // Right-click to remove a placed component
    cell.addEventListener('contextmenu', e => {
      e.preventDefault();
      const placed = cell.querySelector('.component');
      if (placed) placed.remove();
    });
  });
}


// main.js additions and modifications

/**
 * Overlay semi-transparent hints for the target circuit
 */
function addHints(levelData) {
  levelData.placements.forEach(({ x, y, type }) => {
    const cell = document.querySelector(
      `.grid-cell[data-x="${x}"][data-y="${y}"]`
    );
    if (cell) {
      const hint = document.createElement('div');
      hint.classList.add('hint');
      // Use first letter as shorthand; could swap for icons
      hint.textContent = type.charAt(0).toUpperCase();
      cell.appendChild(hint);
    }
  });
}

// Modify initLevel to build grid, then add hints
function initLevel(index) {
  clearInterval(timerInterval);
  elapsedTime = 0;
  timerDisplay.textContent = `${elapsedTime}s`;

  levelDisplay.textContent = index + 1;
  scoreDisplay.textContent = totalScore;

  // Build the grid and overlay hints
  buildGrid(levels[index].gridSize);
  addHints(levels[index]);

  setupDragAndDrop();

  timerInterval = setInterval(() => {
    elapsedTime++;
    timerDisplay.textContent = `${elapsedTime}s`;
  }, 1000);
}

// Enhanced drag-and-drop to support repositioning
function setupDragAndDrop() {
  // Palette items: start drag with type only
  document.querySelectorAll('#palette .component').forEach(comp => {
    comp.addEventListener('dragstart', e => {
      e.dataTransfer.setData(
        'application/json',
        JSON.stringify({ type: comp.dataset.type })
      );
    });
  });

  document.querySelectorAll('.grid-cell').forEach(cell => {
    cell.addEventListener('dragover', e => {
      e.preventDefault();
      cell.classList.add('highlight');
    });
    cell.addEventListener('dragleave', () => {
      cell.classList.remove('highlight');
    });
    cell.addEventListener('drop', e => {
      e.preventDefault();
      cell.classList.remove('highlight');
      let dragData;
      try {
        dragData = JSON.parse(e.dataTransfer.getData('application/json'));
      } catch {
        dragData = { type: e.dataTransfer.getData('text/plain') };
      }
      const { type, originX, originY } = dragData;
      // If we're moving an existing component, remove its original
      if (originX && originY) {
        const originCell = document.querySelector(
          `.grid-cell[data-x="${originX}"][data-y="${originY}"]`
        );
        const originComp = originCell?.querySelector('.component');
        if (originComp) originComp.remove();
      }
      placeComponent(cell, type);
    });
    // Right-click removal remains
    cell.addEventListener('contextmenu', e => {
      e.preventDefault();
      const placed = cell.querySelector('.component');
      if (placed) placed.remove();
    });
  });
}

// Update placeComponent to make the dropped item draggable for reposition
function placeComponent(cell, type) {
  const existing = cell.querySelector('.component');
  if (existing) existing.remove();

  const comp = document.createElement('div');
  comp.classList.add('component');
  comp.textContent = type.charAt(0).toUpperCase() + type.slice(1);
  comp.dataset.type = type;
  comp.setAttribute('draggable', 'true');

  // Register dragstart so we can reposition
  comp.addEventListener('dragstart', e => {
    const originX = cell.dataset.x;
    const originY = cell.dataset.y;
    e.dataTransfer.setData(
      'application/json',
      JSON.stringify({ type, originX, originY })
    );
  });

  cell.appendChild(comp);
}


// main.js additions for toggling hints
// --- Hint Toggle ---
const toggleHintsBtn = document.getElementById('toggle-hints-btn');
let hintsVisible = true;

toggleHintsBtn.addEventListener('click', toggleHints);

/**
 * Show or hide all hint overlays and update button text
 */
function toggleHints() {
  hintsVisible = !hintsVisible;
  document.querySelectorAll('.hint').forEach(hint => {
    hint.style.display = hintsVisible ? 'flex' : 'none';
  });
  toggleHintsBtn.textContent = hintsVisible ? 'Hide Hints' : 'Show Hints';
}

// Ensure hints start visible when a level loads
// (initLevel will call addHints which renders hints, toggleHintsBtn text already set)




window.addEventListener('DOMContentLoaded', () => {
  const instr = document.getElementById('instructions-overlay');
  const startBtn = document.getElementById('start-btn');
  startBtn.addEventListener('click', () => {
    instr.style.display = 'none';
    console.log("aaa")
  });
});
