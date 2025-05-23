(function() {
    StateManager.subscribe('battleResult', ({ taskId, result, xpGain, goldGain, hpLoss }) => {
        const s = StateManager.getState();
        let { xp, gold, level, hp, maxHp } = s.player;
        gold += goldGain; xp += xpGain; hp = Math.max(hp - hpLoss, 0);
        
        const thr = level * 100;
        if (xp >= thr) { xp -= thr; level++; maxHp += 20; hp = maxHp; }
        
        const player = { ...s.player, xp, gold, level, hp, maxHp };
        StateManager.setState({ ...s, player });
        Persistence.saveState();
        StateManager.dispatch('stateUpdated', { taskId, result, xpGain, goldGain, hpLoss, player });
    });
})();