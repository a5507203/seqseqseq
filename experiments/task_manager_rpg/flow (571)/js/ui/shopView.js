(function() {
    const c = document.getElementById('view-shop');
    function render() {
        const { s: { player, items } } = StateManager.getState();
        c.innerHTML = '';

        const h = document.createElement('div');
        h.className = 'shop-header';
        h.innerHTML = `<h2>Shop</h2><p>Gold: ${player.gold}</p><p>HP: ${player.hp}/${player.maxHp}</p>`;
        c.appendChild(h);

        const list = document.createElement('div');
        list.className = 'shop-items';

        items.filter(i => i.type === 'potion').forEach(i => {
            const card = document.createElement('div');
            card.className = 'shop-item';
            card.innerHTML = `<h3>${i.name}</h3><p>Restores ${i.effect.hpRestore} HP</p><p>Price: ${i.price}g</p>`;
            const btn = document.createElement('button');
            btn.textContent = 'Buy';
            btn.disabled = player.gold < i.price || player.hp >= player.maxHp;
            btn.addEventListener('click', () => ShopManager.purchase(i.id));
            card.appendChild(btn);
            list.appendChild(card);
        });

        c.appendChild(list);
    }

    function init() {
        StateManager.subscribe('stateLoaded', render);
        StateManager.subscribe('shopUpdated', render);
        document.getElementById('nav-shop').addEventListener('click', () => {
            showView('view-shop');
            render();
        });
    }
    window.addEventListener('DOMContentLoaded', init);
})();
