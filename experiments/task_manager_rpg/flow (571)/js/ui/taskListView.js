(function() {
    const c = document.getElementById('view-tasks');
    function init() {
        c.innerHTML = `
      <h2>Quests</h2>
      <form id="task-form">
        <input type="text" id="task-title" placeholder="Quest title" required/>
        <input type="text" id="task-desc" placeholder="Description" required/>
        <button type="submit">Add Quest</button>
      </form>
      <ul id="task-list"></ul>`;
        
        const f = c.querySelector('#task-form'), 
              ti = c.querySelector('#task-title'), 
              di = c.querySelector('#task-desc');
              
        f.addEventListener('submit', e => {
            e.preventDefault();
            TaskManager.addTask({ title: ti.value.trim(), description: di.value.trim() });
            ti.value = '';
            di.value = '';
        });

        StateManager.subscribe('stateLoaded', s => render(s.tasks));
        StateManager.subscribe('taskAdded', t => append(t));
        StateManager.subscribe('taskCompleted', () => render(StateManager.getState().tasks));
    }

    function render(tasks) {
        const ul = c.querySelector('#task-list'); 
        ul.innerHTML = ''; 
        tasks.forEach(append);
    }

    function append(t) {
        const ul = c.querySelector('#task-list'), 
              li = document.createElement('li');
              
        li.id = t.id; 
        li.className = t.status === 'completed' ? 'completed' : '';
        li.innerHTML = `<div><strong>${t.title}</strong><br/><small>${t.description}</small></div>`;
        
        const b = document.createElement('button');
        b.textContent = t.status === 'pending' ? 'Complete' : 'Done';
        b.className = 'complete';
        b.disabled = t.status === 'completed';
        b.addEventListener('click', () => TaskManager.completeTask(t.id)); 
        
        li.appendChild(b); 
        ul.appendChild(li);
    }
    document.getElementById('nav-tasks').addEventListener('click', () => showView('view-tasks'));
    window.addEventListener('DOMContentLoaded', init);
})();