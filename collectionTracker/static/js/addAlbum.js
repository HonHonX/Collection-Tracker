document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.album-item').forEach(albumItem => {
        const inCollection = albumItem.dataset.inCollection === 'true';
        const addIcon = albumItem.querySelector('.album-controls .icon');
        if (inCollection) {
            addIcon.classList.add('disabled');
            addIcon.alt = "Already added";
        } else {
            addIcon.addEventListener('click', function () {
                const albumId = albumItem.dataset.albumId;
                const albumName = albumItem.dataset.albumName;
                const albumType = albumItem.dataset.albumType;
                const releaseDate = albumItem.dataset.releaseDate;
                const imageUrl = albumItem.dataset.imageUrl;
                const artistName = albumItem.dataset.artistName;

                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                fetch('/collection/add_album/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        album_id: albumId,
                        album_name: albumName,
                        album_type: albumType,
                        release_date: releaseDate,
                        image_url: imageUrl,
                        artist_name: artistName, // Include artist name
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                    } else {
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        }
    });
});
