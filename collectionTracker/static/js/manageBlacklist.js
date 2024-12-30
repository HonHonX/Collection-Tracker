document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.album-item').forEach(albumItem => {
        const inBlacklist = albumItem.dataset.inBlacklist === 'true';
        const inWishlist = albumItem.dataset.inWishlist === 'true';
        const inCollection = albumItem.dataset.inCollection === 'true';
        const controlIcon = albumItem.querySelector('#blacklist-control-icon');

        // Initialize the album state based on blacklist status
        updateAlbumState(albumItem, inBlacklist);

        // Set event listener for handling album blacklist actions
        setControlIconClickListener(albumItem, controlIcon, inBlacklist, inWishlist, inCollection);
    });

    // Function to update the UI based on whether the album is in the blacklist
    function updateAlbumState(albumItem, inBlacklist) {
        const controlIcon = albumItem.querySelector('#blacklist-control-icon');

        if (inBlacklist) {
            albumItem.dataset.inBlacklist = 'true';
            controlIcon.classList.add('wanted');
            controlIcon.alt = "Already added";
            controlIcon.src = "/static/icons/blacklist_remove.svg"; // 'remove' icon
        } else {
            albumItem.dataset.inBlacklist = 'false';
            controlIcon.classList.remove('wanted');
            controlIcon.alt = "Add to blacklist";
            controlIcon.src = "/static/icons/blacklist_add.svg"; // 'add' icon
        }

        // Update background color based on the album's state
        updateAlbumBackgroundColor(albumItem);
    }

    // Function to update the background color based on album state
    function updateAlbumBackgroundColor(albumItem) {
        const inBlacklist = albumItem.dataset.inBlacklist === 'true';
        const inWishlist = albumItem.dataset.inWishlist === 'true';
        const inCollection = albumItem.dataset.inCollection === 'true';

        if (inBlacklist) {
            albumItem.style.backgroundColor = 'var(--neutral70)';
        } else if (inWishlist && inCollection) {
            albumItem.style.backgroundColor = 'var(--accentVariantA100)';
        } else if (inWishlist) {
            albumItem.style.backgroundColor = 'var(--accentVariantB100)';
        } else if (inCollection) {
            albumItem.style.backgroundColor = 'var(--accent100)';
        } else {
            albumItem.style.backgroundColor = 'var(--neutral100)';
        }
    }

    // Function to set the event listener for control icon
    function setControlIconClickListener(albumItem, controlIcon, inBlacklist, inWishlist, inCollection) {
        // Remove existing event listener to prevent duplicates
        controlIcon.removeEventListener('click', handleAlbumClick);

        // Attach the correct event listener based on the current state of the album
        controlIcon.addEventListener('click', handleAlbumClick);

        function handleAlbumClick() {
            const albumId = albumItem.dataset.albumId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Dynamically check the album's current status
            const currentInBlacklist = albumItem.dataset.inBlacklist === 'true';
            const currentInWishlist = albumItem.dataset.inWishlist === 'true';
            const currentInCollection = albumItem.dataset.inCollection === 'true';

            // If album is in blacklist, remove it
            if (currentInBlacklist) {
                if (!confirm('Are you sure you want to remove this album from your blacklist?')) {
                    return;
                }

                // Send the remove request to the backend
                fetch('/collection/manage_album/blacklist/remove/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ album_id: albumId })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update the UI and state accordingly
                        updateAlbumState(albumItem, false);
                    } else {
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));

            } else {
                // If the album is not in the blacklist, add it
                const promises = [];

                // If the album is in wishlist or collection, remove from those lists first
                if (currentInWishlist) {
                    promises.push(fetch('/collection/manage_album/wishlist/remove/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                        },
                        body: JSON.stringify({ album_id: albumId })
                    }));
                }

                if (currentInCollection) {
                    promises.push(fetch('/collection/manage_album/collection/remove/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                        },
                        body: JSON.stringify({ album_id: albumId })
                    }));
                }

                // After removal, add to blacklist
                Promise.all(promises)
                    .then(() => {
                        return fetch('/collection/manage_album/blacklist/add/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken,
                            },
                            body: JSON.stringify({
                                album_id: albumId,
                                album_name: albumItem.dataset.albumName,
                                album_type: albumItem.dataset.albumType,
                                release_date: albumItem.dataset.releaseDate,
                                image_url: albumItem.dataset.imageUrl,
                                artist_name: albumItem.dataset.artistName
                            })
                        });
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Update the UI and state after adding to blacklist
                            updateAlbumState(albumItem, true);
                        } else {
                            alert(data.error || data.message);
                        }
                    })
                    .catch(error => console.error('Error:', error));
            }
        }
    }
});
