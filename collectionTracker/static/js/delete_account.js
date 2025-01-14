document.addEventListener('DOMContentLoaded', function() {
    const deleteForm = document.getElementById('delete-account-form');
    
    deleteForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (confirm('Are you sure you want to delete your account? We will sent you an e-mail for confirmation.')) {
            fetch(this.action, {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                // Optional: Redirect to home page after closing the alert
                // window.location.href = '/';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again later.');
            });
        }
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
