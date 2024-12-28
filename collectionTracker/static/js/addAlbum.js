document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.album-item').forEach(albumItem => {
        const inCollection = albumItem.dataset.inCollection === 'true';
        const addIcon = albumItem.querySelector('#add-icon');

        if (inCollection) {
            updateAlbumState(albumItem, true);
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
                        // Update the UI to reflect the album is now in the collection
                        updateAlbumState(albumItem, true);
                    } else {
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        }
    });

    function updateAlbumState(albumItem, inCollection) {
        const addIcon = albumItem.querySelector('#add-icon');
        if (inCollection) {
            albumItem.dataset.inCollection = 'true';
            addIcon.classList.add('disabled');
            
            addIcon.alt = "Already added";
            addIcon.src = "/static/icons/remove.svg"; // Optionally, change icon
        } else {
            albumItem.dataset.inCollection = 'false';
            addIcon.classList.remove('disabled');
            addIcon.alt = "Add to collection";
            addIcon.src = "/static/icons/add.svg"; // Optionally, reset icon
        }
    }
});
