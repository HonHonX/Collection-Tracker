document.addEventListener('DOMContentLoaded', function() {
    const followButton = document.getElementById('follow-button');
    if (followButton) {
        followButton.addEventListener('click', function() {
            const artistId = this.getAttribute('data-artist-id');
            fetch(followButton.dataset.url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': followButton.dataset.csrf
                },
                body: JSON.stringify({ artist_id: artistId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.textContent = this.textContent.trim() === 'Follow' ? 'Unfollow' : 'Follow';
                } else {
                    alert(data.error);
                }
            });
        });
    }
});
