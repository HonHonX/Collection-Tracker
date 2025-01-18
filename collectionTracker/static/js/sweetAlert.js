<script>
document.addEventListener('DOMContentLoaded', function () {
    const notification = {
        title: "Congratulations!",
        text: "{{ notification.message }}",
        imageUrl: "{{ notification.user_badge.badge.image_url }}",
        imageWidth: 100,
        imageHeight: 100,
        timer: 3000,
        timerProgressBar: true,
        showConfirmButton: false,
    };

    Swal.fire(notification).then(() => {
        fetch(`/stats/delete_notification/{{ notification.id }}/`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}",
                "Content-Type": "application/json",
            },
        }).then((response) => {
            if (!response.ok) {
                console.error(`Failed to delete notification: {{ notification.id }}`);
            } else {
                console.log(`Notification deleted: {{ notification.id }}`);
            }
        });
    });
});
</script>
