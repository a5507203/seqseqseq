(function() {
    const BE = {
        init() { StateManager.subscribe('taskCompleted', this.onTaskCompleted.bind(this)); },
        onTaskCompleted({ taskId }) {
            const { s: { tasks, monsters, player } } = { s: StateManager.getState() };
            const t = tasks.find(t => t.id === taskId);
            if (!t) return;
            const m = monsters.find(m => m.id === t.monsterId);
            const orig = player.hp;
            const { result, remainingHp } = this.simulateBattle(player, m);
            StateManager.dispatch('battleResult', {
                taskId, result,
                xpGain: result === 'win' ? m.xpReward : 0,
                goldGain: result === 'win' ? m.goldReward : 0,
                hpLoss: orig - remainingHp
            });
        },
        simulateBattle(p, m) {
            let pHp = p.hp, mHp = m.hp;
            const pAtk = p.level * 10, pDef = p.level * 5,
                mAtk = m.attack, mDef = m.defense;

            while (pHp > 0 && mHp > 0) {
                mHp -= Math.max(pAtk - mDef, 1);
                if (mHp <= 0) break;
                pHp -= Math.max(mAtk - pDef, 1);
            }
            return { result: pHp > 0 ? 'win' : 'lose', remainingHp: Math.max(pHp, 0) };
        }
    }; BE.init(); window.BattleEngine = BE;
})();