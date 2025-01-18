document.addEventListener('DOMContentLoaded', function() {
    fetch('/stats/notifications/')
        .then(response => response.json())
        .then(data => {
            if (data.notifications && data.notifications.length > 0) {
                console.log('Notifications fetched:', data.notifications);
                let showNotification = (index) => {
                    if (index < data.notifications.length) {
                        let notification = data.notifications[index];
                        Swal.fire({
                            title: 'Congratulations!',
                            text: notification.message,
                            imageUrl: notification.badge_image_url,
                            imageWidth: 100,
                            imageHeight: 100,
                            timer: 3000,
                            timerProgressBar: true,
                            showConfirmButton: false,
                        }).then(() => {
                            console.log('Deleting notification:', notification.id);
                            fetch(`/stats/delete_notification/${notification.id}/`, {
                                method: 'DELETE',
                                headers: {
                                    'X-CSRFToken': '{{ csrf_token }}',
                                    'Content-Type': 'application/json'
                                }
                            }).then(response => {
                                if (!response.ok) {
                                    console.error('Failed to delete notification:', notification.id);
                                } else {
                                    console.log('Notification deleted:', notification.id);
                                }
                                showNotification(index + 1);
                            });
                        });
                    }
                };
                showNotification(0);
            } else {
                console.log('No notifications to show.');
            }
        })
        .catch(error => {
            console.error('Error fetching notifications:', error);
        });
});