document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.album-item').forEach(albumItem => {
        const inCollection = albumItem.dataset.inCollection === 'true'; 
        const inBlacklist = albumItem.dataset.inBlacklist === 'true'; 
        const controlIcon = albumItem.querySelector('#control-icon');

        if (inBlacklist) {
            albumItem.dataset.inCollection = 'false'; 
            updateAlbumState(albumItem, false);  
        }

        updateAlbumState(albumItem, inCollection);

        setControlIconClickListener(albumItem, controlIcon, inCollection);
    });

    function updateAlbumState(albumItem, inCollection) {
        const controlIcon = albumItem.querySelector('#control-icon');

        if (inCollection) {
            albumItem.dataset.inCollection = 'true';
            controlIcon.classList.add('collected');
            controlIcon.alt = "Already added";
            controlIcon.src = "/static/icons/remove.svg"; // Change to 'remove' icon
        } else {
            albumItem.dataset.inCollection = 'false';
            controlIcon.classList.remove('collected');
            controlIcon.alt = "Add to collection";
            controlIcon.src = "/static/icons/add.svg"; // Reset to 'add' icon
        }

        updateAlbumBackgroundColor(albumItem);
    }

    function updateAlbumBackgroundColor(albumItem) {
        const inWishlist = albumItem.dataset.inWishlist === 'true';
        const inCollection = albumItem.dataset.inCollection === 'true';
        const inBlacklist = albumItem.dataset.inBlacklist === 'true';

        if (inWishlist && inCollection) {
            albumItem.style.backgroundColor = 'var(--accentVariantA100)';
        } else if (inWishlist) {
            albumItem.style.backgroundColor = 'var(--accentVariantB100)';
        } else if (inCollection) {
            albumItem.style.backgroundColor = 'var(--accent100)';
        } else if (inBlacklist) {
            albumItem.style.backgroundColor = 'var(--neutral70)';
        } else {
            albumItem.style.backgroundColor = 'var(--neutral100)';
        }
    }

    function setControlIconClickListener(albumItem, controlIcon, inCollection) {
        controlIcon.removeEventListener('click', handleAlbumClick);
        controlIcon.addEventListener('click', handleAlbumClick);

        function handleAlbumClick() {
            const albumId = albumItem.dataset.albumId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const currentInCollection = albumItem.dataset.inCollection === 'true';
        
            if (currentInCollection) {
                if (!confirm('Are you sure you want to remove this album from your collection?')) return;
                fetch('/collection/remove_album/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ album_id: albumId }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateAlbumState(albumItem, false); // Update state to reflect removal
                    } else {
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
            } else {
                const albumName = albumItem.dataset.albumName;
                const albumType = albumItem.dataset.albumType;
                const releaseDate = albumItem.dataset.releaseDate;
                const imageUrl = albumItem.dataset.imageUrl;
                const artistName = albumItem.dataset.artistName;

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
                        artist_name: artistName,
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateAlbumState(albumItem, true); // Update state to reflect addition
                    } else {
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));                
            }
        }
    }
});
