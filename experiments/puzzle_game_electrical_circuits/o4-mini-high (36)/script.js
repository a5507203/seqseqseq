// script.js
const puzzles = [
  { target: 'R at 0,0 to 0,1', solution: [{x:0,y:0,t:'resistor'}, {x:0,y:1,t:'resistor'}] },
  // ... define 20 puzzles increasing complexity
];
let level=0, startTime, timerInterval, score=0;
const gridSize = 8;
const boardEl = document.getElementById('board');
const levelEl = document.getElementById('level');
const timerEl = document.getElementById('timer');
const scoreEl = document.getElementById('score');
const targetDisplay = document.getElementById('target-display');
function initBoard(){
  boardEl.innerHTML='';
  for(let y=0;y<gridSize;y++){
    for(let x=0;x<gridSize;x++){
      const cell = document.createElement('div');
      cell.classList.add('cell');
      cell.dataset.x=x; cell.dataset.y=y;
      cell.addEventListener('dragover', e=>e.preventDefault());
      cell.addEventListener('drop', onDrop);
      boardEl.appendChild(cell);
    }
  }
}
function onDrop(e){
  e.preventDefault();
  const type=e.dataTransfer.getData('type');
  const cell=e.currentTarget;
  cell.innerHTML = `<div class="placed">${type[0].toUpperCase()}</div>`;
  cell.dataset.type=type;
}
document.querySelectorAll('.component').forEach(c=>{
  c.addEventListener('dragstart', e=>{
    e.dataTransfer.setData('type',c.dataset.type);
  });
});
function startTimer(){
  startTime=Date.now();
  timerInterval=setInterval(()=>{
    const s=Math.floor((Date.now()-startTime)/1000);
    timerEl.textContent=`Time: ${s}s`;
  },1000);
}
function loadLevel(){
  clearInterval(timerInterval);
  initBoard();
  levelEl.textContent = `Level: ${level+1}`;
  targetDisplay.textContent = puzzles[level].target;
  startTimer();
}
document.getElementById('check-btn').addEventListener('click', ()=>{
  clearInterval(timerInterval);
  const placed = [];
  document.querySelectorAll('.cell').forEach(c=>{
    if(c.dataset.type) placed.push({x:+c.dataset.x,y:+c.dataset.y,t:c.dataset.type});
  });
  const sol = puzzles[level].solution;
  const correct = JSON.stringify(placed)==JSON.stringify(sol);
  const timeSec=Math.floor((Date.now()-startTime)/1000);
  if(correct){
    const levelScore=Math.max(0,100-timeSec);
    score+=levelScore;
    alert(`Correct! +${levelScore} points`);
    scoreEl.textContent=`Score: ${score}`;
    level++;
    if(level<puzzles.length) loadLevel();
    else alert('You completed all puzzles!');
  } else alert('Incorrect, try again.');
});
document.getElementById('reset-btn').addEventListener('click', loadLevel);
// init
loadLevel();
