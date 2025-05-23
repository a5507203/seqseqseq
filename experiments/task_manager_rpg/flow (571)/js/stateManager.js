const StateManager = (function() {
    let state = {};
    const listeners = {};
    function subscribe(event, cb) {
        (listeners[event] || (listeners[event] = [])).push(cb);
    }
    function dispatch(event, p) {
        (listeners[event] || []).forEach(cb => cb(p));
    }
    function setState(s) {
        state = s;
        dispatch('stateChanged', state);
    }
    function getState() {
        return state;
    }
    return { subscribe, dispatch, setState, getState };
})();
window.StateManager = StateManager;