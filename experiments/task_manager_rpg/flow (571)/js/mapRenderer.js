const MapRenderer = (function() {
    let map, markers = new Map();
    function init(c) {
        map = L.map(c).setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors', maxZoom: 19
        }).addTo(map);
        StateManager.subscribe('stateLoaded', renderAll);
        StateManager.subscribe('taskAdded', onAdded);
        StateManager.subscribe('taskCompleted', onCompleted);
    }
    function renderAll() {
        clear(); const tasks = StateManager.getState().tasks;
        tasks.filter(t => t.status === 'pending' && t.location).forEach(add);
    }
    function add(t) {
        const m = L.marker([t.location.latitude, t.location.longitude])
            .addTo(map).bindPopup(`<strong>${t.title}</strong>`);
        markers.set(t.id, m); fit();
    }
    function onAdded(t) { if (t.status === 'pending' && t.location) add(t); }
    function onCompleted({ taskId }) {
        const m = markers.get(taskId);
        if (m) { map.removeLayer(m); markers.delete(taskId); fit(); }
    }
    function clear() { markers.forEach(m => map.removeLayer(m)); markers.clear(); }
    function fit() {
        if (markers.size) {
            const g = L.featureGroup([...markers.values()]);
            map.fitBounds(g.getBounds(), { padding: [40, 40] });
        }
    }
    function invalidate() { if (map) map.invalidateSize(); }
    return { init, invalidate };
})();
window.MapRenderer = MapRenderer;