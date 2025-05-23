(function() {
    const c = document.getElementById('view-battle');
    function init() {
        c.innerHTML = `<h2>Battle Log</h2><div class="battle-log" id="battle-log"></div><div id="battle-outcome" class="battle-outcome"></div>`;
        StateManager.subscribe('stateUpdated', update);
    }
    function update({ taskId, result, xpGain, goldGain, hpLoss }) {
        const log = document.getElementById('battle-log'),
              out = document.getElementById('battle-outcome');
        const t = new Date().toLocaleTimeString();
        log.innerHTML += `[${t}] Quest ${taskId} ${result.toUpperCase()}: +${xpGain} XP, +${goldGain}g, -${hpLoss} HP<br/>`;
        out.textContent = `Last Battle: ${result === 'win' ? 'Victory!' : 'Defeat'}`;
        out.className = `battle-outcome ${result === 'win' ? 'success' : 'failure'}`;
    }
    document.getElementById('nav-battle').addEventListener('click', () => showView('view-battle'));
    window.addEventListener('DOMContentLoaded', init);
})();