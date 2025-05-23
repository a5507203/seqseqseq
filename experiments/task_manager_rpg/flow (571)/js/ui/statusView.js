(function() {
    const c = document.getElementById('view-status');
    function render() {
        const { player } = StateManager.getState();
        c.innerHTML = '<h2>Status</h2><div class="status-grid"></div>';
        const g = c.querySelector('.status-grid');
        [
            { label: 'Level', value: player.level },
            { label: 'XP', value: player.xp + '/' + (player.level * 100) },
            { label: 'Gold', value: player.gold },
            { label: 'HP', value: player.hp + '/' + player.maxHp }
        ].forEach(s => {
            const card = document.createElement('div'); 
            card.className = 'status-card';
            card.innerHTML = `<h4>${s.label}</h4><p>${s.value}</p>`;
            g.appendChild(card);
        });
    }
    function init() {
        StateManager.subscribe('stateLoaded', render);
        StateManager.subscribe('stateUpdated', render);
        document.getElementById('nav-status').addEventListener('click', () => {
            showView('view-status');
            render();
        });
    }
    window.addEventListener('DOMContentLoaded', init);
})();