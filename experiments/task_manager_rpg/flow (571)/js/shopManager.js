const ShopManager = (function() {
    function purchase(itemId) {
        const s = StateManager.getState();
        const item = s.items.find(i => i.id === itemId && i.type === 'potion');
        if (!item || s.player.gold < item.price) return;

        const gold = s.player.gold - item.price;
        const hp = Math.min(s.player.maxHp, s.player.hp + (item.effect.hpRestore || 0));
        const player = { ...s.player, gold, hp };
        
        StateManager.setState({ ...s, player });
        StateManager.dispatch('shopUpdated', { itemId, player });
        Persistence.saveState();
    }
    return { purchase };
})();
window.ShopManager = ShopManager;