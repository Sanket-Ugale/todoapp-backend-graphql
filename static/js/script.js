$(document).ready(function() {
    const apiUrl = 'http://127.0.0.1/api/';

    // Function to get the CSRF token from the cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // Setup AJAX to include CSRF token in the headers
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    function fetchTodos() {
        $.ajax({
            url: apiUrl,
            method: 'GET',
            success: function(data) {
                $('#todoList').empty();
                data.forEach(function(todo) {
                    const todoItem = `<div class="list-group-item list-group-item-action flex-column align-items-start" data-id="${todo.id}">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">${todo.title}</h5>
                            <small>Status: ${todo.status ? 'Complete' : 'Incomplete'}</small>
                        </div>
                        <p class="mb-1">${todo.content}</p>
                        <button class="btn btn-sm btn-warning updateTodoBtn">Update</button>
                        <button class="btn btn-sm btn-danger deleteTodoBtn">Delete</button>
                    </div>`;
                    $('#todoList').append(todoItem);
                });
            },
            error: function(error) {
                console.error('Error fetching To-Dos:', error);
            }
        });
    }

    fetchTodos();

    $('#addTodoForm').submit(function(e) {
        e.preventDefault();
        const title = $('#addTodoTitle').val();
        const content = $('#addTodoContent').val();
        $.ajax({
            url: apiUrl,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ title: title, content: content }),
            success: function(response) {
                $('#addTodoModal').modal('hide');
                fetchTodos();
            },
            error: function(error) {
                console.error('Error adding To-Do:', error);
            }
        });
    });

    $(document).on('click', '.updateTodoBtn', function() {
        const todoItem = $(this).closest('.list-group-item');
        const id = todoItem.data('id');
        const title = todoItem.find('h5').text();
        const content = todoItem.find('p').text();
        const status = todoItem.find('small').text().includes('Complete');

        $('#updateTodoId').val(id);
        $('#updateTodoTitle').val(title);
        $('#updateTodoContent').val(content);
        $('#updateTodoStatus').val(status);

        $('#updateTodoModal').modal('show');
    });

    $('#updateTodoForm').submit(function(e) {
        e.preventDefault();
        const id = $('#updateTodoId').val();
        const title = $('#updateTodoTitle').val();
        const content = $('#updateTodoContent').val();
        const status = $('#updateTodoStatus').val() === 'true';

        $.ajax({
            url: apiUrl,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({ id: id, title: title, content: content, status: status }),
            success: function(response) {
                $('#updateTodoModal').modal('hide');
                fetchTodos();
            },
            error: function(error) {
                console.error('Error updating To-Do:', error);
            }
        });
    });

    $(document).on('click', '.deleteTodoBtn', function() {
        const id = $(this).closest('.list-group-item').data('id');

        $.ajax({
            url: apiUrl,
            method: 'DELETE',
            contentType: 'application/json',
            data: JSON.stringify({ id: id }),
            success: function(response) {
                fetchTodos();
            },
            error: function(error) {
                console.error('Error deleting To-Do:', error);
            }
        });
    });
});