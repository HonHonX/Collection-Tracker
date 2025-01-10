document.addEventListener('DOMContentLoaded', function() {
    const followBlocks = document.querySelectorAll('.follow-block');
    followBlocks.forEach(block => {
        const followButton = block.querySelector('#follow-button');
        
        followButton.addEventListener('click', function() {
            const artistId = block.getAttribute('data-artist-id');
            const url = block.getAttribute('data-follow-url');

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': followButton.dataset.csrf
                },
                body: JSON.stringify({
                    artist_id: artistId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (this.textContent.trim() === 'Follow') {
                        this.textContent = 'Unfollow';
                    } else {
                        this.textContent = 'Follow';
                        // Remove the artist card from the DOM
                        block.closest('.artist-card').remove();
                    }
                } else {
                    alert(data.error);
                }
            });
        });
    });
});