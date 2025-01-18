document.addEventListener('DOMContentLoaded', function() {
    const deleteForm = document.getElementById('delete-account-form');
    
    deleteForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        Swal.fire({
            title: "Are you sure?",
            text: "Are you sure you want to delete your account? We will send you an e-mail for confirmation.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'No, keep it'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(this.action, {
                    method: 'POST',
                    body: new FormData(this),
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    Swal.fire("Success", data.message, "success");
                    window.location.href = '/';
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire("Error", "An error occurred. Please try again later.", "error");
                });
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
