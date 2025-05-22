

// --- Player State ---
const player = {
  hp: 100,
  xp: 0,
  gold: 0
};

// --- DOM Elements ---
const hpEl = document.getElementById('hp');
const xpEl = document.getElementById('xp');
const goldEl = document.getElementById('gold');

const todoForm = document.getElementById('todo-form');
const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');

const mapDiv = document.getElementById('map');

const battleModal = document.getElementById('battle-modal');
const battleLog = document.getElementById('battle-log');
const battleCloseBtn = document.getElementById('battle-close');

const shopModal = document.getElementById('shop-modal');
const openShopBtn = document.getElementById('open-shop');
const buyPotionBtn = document.getElementById('buy-potion');
const shopCloseBtn = document.getElementById('shop-close');

// --- Utilities ---
function updateStats() {
  hpEl.textContent = `HP: ${player.hp}`;
  xpEl.textContent = `XP: ${player.xp}`;
  goldEl.textContent = `Gold: ${player.gold}`;
}

function getRandomBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// --- Quest Management ---
let questIdCounter = 0;

todoForm.addEventListener('submit', e => {
  e.preventDefault();
  const text = todoInput.value.trim();
  if (!text) return;
  addQuest(text);
  todoInput.value = '';
});

function addQuest(name) {
  const id = ++questIdCounter;
  // List entry
  const li = document.createElement('li');
  const chk = document.createElement('input');
  chk.type = 'checkbox';
  chk.dataset.id = id;
  const span = document.createElement('span');
  span.textContent = name;
  li.append(chk, ' ', span);
  todoList.appendChild(li);

  // Map marker
  const marker = document.createElement('div');
  marker.className = 'quest-marker';
  marker.dataset.id = id;
  marker.title = name;
  // Random position inside map
  const x = getRandomBetween(10, mapDiv.clientWidth - 30);
  const y = getRandomBetween(10, mapDiv.clientHeight - 30);
  marker.style.left = `${x}px`;
  marker.style.top = `${y}px`;
  mapDiv.appendChild(marker);

  // Event: complete quest checkbox
  chk.addEventListener('change', () => {
    if (chk.checked) startBattle(id, name, marker, li);
  });
}

// --- Battle Simulation ---
function startBattle(id, questName, markerEl, listItemEl) {
  battleLog.innerHTML = `<p>Engaging monster for quest: <strong>${questName}</strong>...</p>`;
  battleModal.classList.remove('hidden');

  // Simple random outcome after delay
  setTimeout(() => {
    const success = Math.random() > 0.4; // 60% win chance
    if (success) {
      const gainedXp = getRandomBetween(10, 20);
      const gainedGold = getRandomBetween(5, 15);
      player.xp += gainedXp;
      player.gold += gainedGold;
      battleLog.innerHTML += `<p style='color:green;'>Victory! +${gainedXp} XP, +${gainedGold} Gold.</p>`;
    } else {
      const lostHp = getRandomBetween(10, 25);
      player.hp = Math.max(0, player.hp - lostHp);
      battleLog.innerHTML += `<p style='color:red;'>Defeated! -${lostHp} HP.</p>`;
    }
    updateStats();

    // Remove quest from UI
    markerEl.remove();
    listItemEl.remove();
  }, 1000);
}

battleCloseBtn.addEventListener('click', () => {
  battleModal.classList.add('hidden');
});

// --- Shop Logic ---
openShopBtn.addEventListener('click', () => {
  shopModal.classList.remove('hidden');
});
shopCloseBtn.addEventListener('click', () => {
  shopModal.classList.add('hidden');
});
buyPotionBtn.addEventListener('click', () => {
  if (player.gold >= 10) {
    player.gold -= 10;
    player.hp += 20;
    updateStats();
  } else {
    alert('Not enough gold!');
  }
});

// --- Initialization ---
updateStats();
