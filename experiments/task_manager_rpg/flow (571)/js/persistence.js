

const Persistence = (function() {
    const KEY = 'todoRpgState';
    function getDefault() {
        return { tasks: [], monsters: [
            { id: 'm1', name: 'Goblin', hp: 50, attack: 8, defense: 3, xpReward: 20, goldReward: 10 },
            { id: 'm2', name: 'Wolf', hp: 60, attack: 10, defense: 4, xpReward: 30, goldReward: 15 },
            { id: 'm3', name: 'Bandit', hp: 80, attack: 12, defense: 6, xpReward: 50, goldReward: 25 }
        ], player: { level: 1, xp: 0, gold: 0, hp: 100, maxHp: 100 }, items: [
            { id: 'p1', name: 'Minor Potion', type: 'potion', effect: { hpRestore: 20 }, price: 10 },
            { id: 'p2', name: 'Major Potion', type: 'potion', effect: { hpRestore: 50 }, price: 25 }
        ] };
    }
    function save() { localStorage.setItem(KEY, JSON.stringify(StateManager.getState())); }
    function load() {
        const raw = localStorage.getItem(KEY);
        StateManager.setState(raw ? JSON.parse(raw) : getDefault());
        StateManager.dispatch('stateLoaded', StateManager.getState());
    }
    return { saveState: save, loadState: load };
})();
window.Persistence = Persistence;
window.addEventListener('DOMContentLoaded', Persistence.loadState);


