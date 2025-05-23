(function() {
    function init() { MapRenderer.init(document.getElementById('view-map')); }
    window.showView = window.showView || function(id) {
        document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
        const v = document.getElementById(id);
        v.classList.remove('hidden');
        if (id === 'view-map') setTimeout(() => MapRenderer.invalidate(), 0);
    };
    document.getElementById('nav-map').addEventListener('click', () => showView('view-map'));
    window.addEventListener('DOMContentLoaded', init);
})();