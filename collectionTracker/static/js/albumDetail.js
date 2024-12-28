document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('edit-description-form');
    const descriptionInput = document.getElementById('description');  // Textarea element to hold the description

    // Function to show browser notification
    function showNotification(message) {
        // Check if the browser supports notifications and if permission is granted
        if (Notification.permission === 'granted') {
            new Notification(message);  // Show notification with the message
        } else if (Notification.permission !== 'denied') {
            // Ask for permission to show notifications if not already denied
            Notification.requestPermission().then(function(permission) {
                if (permission === 'granted') {
                    new Notification(message);  // Show notification if permission is granted
                }
            });
        }
    }

    if (form) {
        form.onsubmit = function(e) {
            e.preventDefault();  // Prevent the default form submission (which causes page reload)

            let description = descriptionInput.value;  // Get the value from the textarea

            fetch(form.action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: `description=${description}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success notification
                    showNotification('Note saved successfully!');
                } else {
                    // Show error notification
                    showNotification('Error saving the note. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('There was an error saving the note.');
            });
        };
    }
});
