document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.album-item').forEach(albumItem => {
        const inCollection = albumItem.dataset.inCollection === 'true'; // Check initial state of the album
        const controlIcon = albumItem.querySelector('#control-icon');

        console.log("Initial inCollection state:", inCollection); // Debugging line

        // Initialize the state based on whether the album is in the collection or not
        updateAlbumState(albumItem, inCollection);

        // Attach the correct event listener based on the album's state
        setControlIconClickListener(albumItem, controlIcon, inCollection);
    });

    // Funktion, um die UI zu aktualisieren, wenn das Album in beiden (Wishlist und Collection) ist
    function updateAlbumBackgroundColor(albumItem) {
        const inWishlist = albumItem.dataset.inWishlist === 'true';
        const inCollection = albumItem.dataset.inCollection === 'true';

        if (inWishlist && inCollection) {
            albumItem.style.backgroundColor = 'var(--accentVariantA100)'; // Hintergrund, wenn in beiden
        } else if (inWishlist) {
            albumItem.style.backgroundColor = 'var(--accentVariantB100)'; // Wishlist-Hintergrund
        } else if (inCollection) {
            albumItem.style.backgroundColor = 'var(--accent100)'; // Collection-Hintergrund
        } else {
            albumItem.style.backgroundColor = 'var(--neutral100)'; // Standard-Hintergrund
        }
    }

    // Function to update the UI based on whether the album is in the collection
    function updateAlbumState(albumItem, inCollection) {
        const controlIcon = albumItem.querySelector('#control-icon');

        // Debugging log
        console.log(`Updating state for album: ${albumItem.dataset.albumId}, In collection: ${inCollection}`);

        if (inCollection) {
            albumItem.dataset.inCollection = 'true';
            controlIcon.classList.add('collected');
            controlIcon.alt = "Already added";
            controlIcon.src = "/static/icons/remove.svg"; // Change the icon to 'remove'
        } else {
            albumItem.dataset.inCollection = 'false';
            controlIcon.classList.remove('collected');
            controlIcon.alt = "Add to collection";
            controlIcon.src = "/static/icons/add.svg"; // Reset to 'add' icon
        }

        updateAlbumBackgroundColor(albumItem); // Hintergrundfarbe aktualisieren
    }

    // Function to set the appropriate event listener for the control icon
    function setControlIconClickListener(albumItem, controlIcon, inCollection) {
        // Remove any existing event listener to avoid duplicates
        controlIcon.removeEventListener('click', handleAlbumClick);

        inCollection = albumItem.dataset.inCollection === 'true'; 

        // Attach the correct event listener based on the album's current inCollection state
        controlIcon.addEventListener('click', handleAlbumClick);

        function handleAlbumClick() {
            const albumId = albumItem.dataset.albumId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
            // Dynamically fetch the current state
            const currentInCollection = albumItem.dataset.inCollection === 'true';
        
            console.log(`Clicked on album: ${albumId}. Current in collection: ${currentInCollection}`);
        
            if (currentInCollection) {
                // If the album is already in the collection, remove it
                if (!confirm('Are you sure you want to remove this album from your collection?')) {
                    return;
                }
        
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
                        alert(data.message);

                        const collectionHeader = document.querySelector('.collection-header p');
                        if (collectionHeader) {
                            albumItem.remove();
                        
                            const currentCount = parseInt(collectionHeader.textContent.match(/\d+/)[0], 10);
                            if (currentCount > 1) {
                                collectionHeader.textContent = `You have added ${currentCount - 1} album(s) to your collection.`;
                            } else {
                                collectionHeader.textContent = 'Your collection is empty.';
                            }
                        }
                        
                        updateAlbumState(albumItem, false); // Update the state to reflect removal
                    } else {
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
            } else {
                // If the album is not in the collection, add it
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
                        alert(data.message);
                        updateAlbumState(albumItem, true); // Update the state to reflect addition
                    } else {
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        }
        
    }

});
