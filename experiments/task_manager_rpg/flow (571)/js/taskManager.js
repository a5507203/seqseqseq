
const TaskManager = (function() {
    function rand(mon) { return mon[Math.floor(Math.random() * mon.length)]; }
    function addTask({ title, description }) {
        const s = StateManager.getState();
        const m = rand(s.monsters);
        const t = {
            id: 't-' + Date.now(), title, description, status: 'pending', monsterId: m.id,
            location: { latitude: (Math.random() - 0.5) * 140, longitude: (Math.random() - 0.5) * 360 }
        };
        const ns = { ...s, tasks: s.tasks.concat(t) };
        StateManager.setState(ns);
        StateManager.dispatch('taskAdded', t);
        Persistence.saveState();
    }
    function completeTask(id) {
        const s = StateManager.getState();
        const i = s.tasks.findIndex(t => t.id === id);
        if (i < 0 || s.tasks[i].status === 'completed') return;
        const nt = { ...s.tasks[i], status: 'completed' };
        const tasks = s.tasks.slice(); tasks[i] = nt;
        StateManager.setState({ ...s, tasks });
        StateManager.dispatch('taskCompleted', { taskId: id });
        Persistence.saveState();
    }
    return { addTask, completeTask };
})();
window.TaskManager = TaskManager;