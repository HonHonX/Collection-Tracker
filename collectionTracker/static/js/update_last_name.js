document.addEventListener('DOMContentLoaded', function() {
    const display = document.getElementById('last-name-display');
    const input = document.getElementById('last-name-input');
    const editIcon = document.getElementById('edit-last-name');
    const saveIcon = document.getElementById('save-last-name');

    editIcon.addEventListener('click', function() {
        display.style.display = 'none';
        input.style.display = 'inline';
        editIcon.style.display = 'none';
        saveIcon.style.display = 'inline';
    });

    saveIcon.addEventListener('click', function() {
        const newName = input.value;
        fetch('/update-last-name/', {  // Ersetzen Sie dies mit der korrekten URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({last_name: newName})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                display.textContent = newName;
                display.style.display = 'inline';
                input.style.display = 'none';
                editIcon.style.display = 'inline';
                saveIcon.style.display = 'none';
            } else {
                alert('Failed to update name');
            }
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}