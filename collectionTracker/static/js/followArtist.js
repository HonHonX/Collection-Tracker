document.addEventListener('DOMContentLoaded', function() {
    const followButton = document.getElementById('follow-button');
    if (followButton) {
        followButton.addEventListener('click', function() {
            const artistId = followButton.getAttribute('data-artist-id');
            const artistName = followButton.getAttribute('data-artist-name');
            const artistGenres = followButton.getAttribute('data-artist-genres');
            const artistPopularity = followButton.getAttribute('data-artist-popularity');
            const artistPhotoUrl = followButton.getAttribute('data-artist-photo-url');
            const url = followButton.getAttribute('data-follow-url');

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': followButton.dataset.csrf
                },
                body: JSON.stringify({
                    artist_id: artistId,
                    artist_name: artistName,
                    artist_genres: artistGenres,
                    artist_popularity: artistPopularity,
                    artist_photo_url: artistPhotoUrl
                })
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