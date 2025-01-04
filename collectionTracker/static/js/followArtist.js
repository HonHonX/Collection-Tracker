document.addEventListener('DOMContentLoaded', function() {
    const followBlocks = document.querySelectorAll('.follow-block');
    followBlocks.forEach(block => {
        const followButton = block.querySelector('#follow-button');
        
        followButton.addEventListener('click', function() {
            const artistId = block.getAttribute('data-artist-id');
            const artistName = block.getAttribute('data-artist-name');
            const artistGenres = block.getAttribute('data-artist-genres');
            const artistPopularity = block.getAttribute('data-artist-popularity');
            const artistPhotoUrl = block.getAttribute('data-artist-photo-url');
            const url = block.getAttribute('data-follow-url');

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
    });
});