document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.album-item').forEach(albumItem => {
        const inWishlist = albumItem.dataset.inWishlist === 'true'; // Check initial state of the album
        const inBlacklist = albumItem.dataset.inBlacklist === 'true'; // Check if album is in blacklist
        const controlIcon = albumItem.querySelector('#wishlist-control-icon');

        // Ensure the album is not in the blacklist before adding to wishlist
        if (inBlacklist) {
            albumItem.dataset.inWishlist = 'false'; // Remove from wishlist if in blacklist
            updateAlbumState(albumItem, false);  // Update UI accordingly
        }

        // Initialize the state based on whether the album is in the wishlist or not
        updateAlbumState(albumItem, inWishlist);

        // Attach the correct event listener based on the album's state
        setControlIconClickListener(albumItem, controlIcon, inWishlist);
    });

    // Function to update the UI based on whether the album is in the wishlist
    function updateAlbumState(albumItem, inWishlist) {
        const controlIcon = albumItem.querySelector('#wishlist-control-icon');

        if (inWishlist) {
            albumItem.dataset.inWishlist = 'true';
            controlIcon.classList.add('wanted');
            controlIcon.alt = "Already added";
            controlIcon.src = "/static/icons/wishlist_remove.svg"; // Change icon to 'remove'
        } else {
            albumItem.dataset.inWishlist = 'false';
            controlIcon.classList.remove('wanted');
            controlIcon.alt = "Add to wishlist";
            controlIcon.src = "/static/icons/wishlist_add.svg"; // Reset to 'add' icon
        }

        updateAlbumBackgroundColor(albumItem); 
    }

    // Function to update the background color
    function updateAlbumBackgroundColor(albumItem) {
        const inWishlist = albumItem.dataset.inWishlist === 'true';
        const inCollection = albumItem.dataset.inCollection === 'true';
        const inBlacklist = albumItem.dataset.inBlacklist === 'true';

        if (inWishlist && inCollection) {
            albumItem.style.backgroundColor = 'var(--accentVariantA100)'; // Background if in both
        } else if (inWishlist) {
            albumItem.style.backgroundColor = 'var(--accentVariantB100)'; // Wishlist background
        } else if (inCollection) {
            albumItem.style.backgroundColor = 'var(--accent100)'; // Collection background
        } else if (inBlacklist) {
            albumItem.style.backgroundColor = 'var(--neutral70)'; // Blacklist background
        } else {
            albumItem.style.backgroundColor = 'var(--neutral100)'; // Default background
        }
    }

    // Function to set the appropriate event listener for the control icon
    function setControlIconClickListener(albumItem, controlIcon, inWishlist) {
        controlIcon.removeEventListener('click', handleAlbumClick);
        controlIcon.addEventListener('click', handleAlbumClick);

        function handleAlbumClick() {
            const albumId = albumItem.dataset.albumId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const currentInWishlist = albumItem.dataset.inWishlist === 'true';
        
            if (currentInWishlist) {
                if (!confirm('Are you sure you want to remove this album from your wishlist?')) return;
                fetch('/collection/remove_album_from_wishlist/', {
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
                        updateAlbumState(albumItem, false); // Update the state to reflect removal
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
        
                fetch('/collection/add_album_to_wishlist/', {
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
