const todoList = document.getElementById('todoList');
const todoForm = document.getElementById('todoForm');
const todoTitle = document.getElementById('todoTitle');
const todoContent = document.getElementById('todoContent');
const saveTodo = document.getElementById('saveTodo');
const todoModal = new bootstrap.Modal(document.getElementById('todoModal'));

let todos = [];
let currentTodo = null;

// Load todos from the server
fetch('/api/')
    .then(response => response.json())
    .then(data => {
        todos = data;
        renderTodos();
    })
    .catch(error => console.error('Error:', error));

// Render todos
function renderTodos() {
    todoList.innerHTML = '';
    todos.forEach(todo => {
        const li = document.createElement('li');
        li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
        li.innerHTML = `
            <span>${todo.title}</span>
            <div>
                <button class="btn btn-primary btn-sm me-2" data-bs-toggle="modal" data-bs-target="#todoModal" onclick="editTodo(${todo.id})">Edit</button>
                <button class="btn btn-danger btn-sm" onclick="deleteTodo(${todo.id})">Delete</button>
            </div>
        `;
        todoList.appendChild(li);
    });
}

// Add or update todo
saveTodo.addEventListener('click', () => {
    const title = todoTitle.value.trim();
    const content = todoContent.value.trim();

    if (title && content) {
        if (currentTodo) {
            // Update existing todo
            fetch('/api/', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: currentTodo.id,
                    title: title,
                    content: content,
                    status: false
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentTodo.title = title;
                    currentTodo.content = content;
                    currentTodo = null;
                    renderTodos();
                    todoModal.hide();
                    clearForm();
                } else {
                    console.error('Error:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        } else {
            // Add new todo
            fetch('/api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    content: content
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    todos.push({ id: Date.now(), title: title, content: content, status: false });
                    renderTodos();
                    todoModal.hide();
                    clearForm();
                } else {
                    console.error('Error:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    }
});

// Edit todo
function editTodo(id) {
    currentTodo = todos.find(todo => todo.id === id);
    todoTitle.value = currentTodo.title;
    todoContent.value = currentTodo.content;
    todoModal.show();
}

// Delete todo
function deleteTodo(id) {
    fetch('/api/', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: id
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            todos = todos.filter(todo => todo.id !== id);
            renderTodos();
        } else {
            console.error('Error:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Clear form
function clearForm() {
    todoTitle.value = '';
    todoContent.value = '';
}