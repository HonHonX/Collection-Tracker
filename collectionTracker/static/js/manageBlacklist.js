document.addEventListener('DOMContentLoaded', function () {
    // Loop through each album and update its state (in blacklist)
    document.querySelectorAll('.album-item').forEach(albumItem => {
        const inBlacklist = albumItem.dataset.inBlacklist === 'true'; // Check initial state of the album
        const inWishlist = albumItem.dataset.inWishlist === 'true'; // Check initial state of the album
        const inCollection = albumItem.dataset.inCollection === 'true'; // Check initial state of the album
        const controlIcon = albumItem.querySelector('#blacklist-control-icon');

        console.log("Initial inBlacklist state:", inBlacklist);

        // Initialize the state based on whether the album is in the blacklist or not
        updateAlbumState(albumItem, inBlacklist);

        // Attach the correct event listener based on the album's state
        setControlIconClickListener(albumItem, controlIcon, inBlacklist, inWishlist, inCollection);
    });

    // Function to update the UI based on whether the album is in the blacklist
    function updateAlbumState(albumItem, inBlacklist) {
        const controlIcon = albumItem.querySelector('#blacklist-control-icon');

        // // Debugging log
        // console.log(`Updating state for album: ${albumItem.dataset.albumId}, In blacklist: ${inBlacklist}`);

        if (inBlacklist) {
            albumItem.dataset.inBlacklist = 'true';
            controlIcon.classList.add('wanted');
            controlIcon.alt = "Already added";
            controlIcon.src = "/static/icons/blacklist_remove.svg"; // Change the icon to 'remove'
        } else {
            albumItem.dataset.inBlacklist = 'false';
            controlIcon.classList.remove('wanted');
            controlIcon.alt = "Add to blacklist";
            controlIcon.src = "/static/icons/blacklist_add.svg"; // Reset to 'add' icon
        }

        // Update the background color based on the current state
        updateAlbumBackgroundColor(albumItem); 
    }

    // Function to update the background color
    function updateAlbumBackgroundColor(albumItem) {
        const inBlacklist = albumItem.dataset.inBlacklist === 'true';

        console.log("About to update the album bg - in Blacklist:", inBlacklist)
        // console.log("About to update the album bg - in Wishlist:", inWishlist)
        // console.log("About to update the album bg - in Collection:", inCollection)

        if (inBlacklist) {
            albumItem.style.backgroundColor = 'var(--neutral70)'; // Background if in Blacklist
        } else {
            albumItem.style.backgroundColor = 'var(--neutral100)'; // Default background
        }
    }

    // Function to set the appropriate event listener for the control icon
    function setControlIconClickListener(albumItem, controlIcon, inBlacklist, inWishlist, inCollection) {
        // Remove any existing event listener to avoid duplicates
        controlIcon.removeEventListener('click', handleAlbumClick);

        inBlacklist = albumItem.dataset.inBlacklist === 'true'; 

        // Attach the correct event listener based on the album's current inBlacklist state
        controlIcon.addEventListener('click', handleAlbumClick);

        function handleAlbumClick() {
            const albumId = albumItem.dataset.albumId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
            // Dynamically fetch the current state
            const currentInBlacklist= albumItem.dataset.inBlacklist === 'true';
            const currentInWishlist= albumItem.dataset.inWishlist === 'true';
            const currentInCollection= albumItem.dataset.inCollection === 'true';
        
            // console.log(`Clicked on album: ${albumId}. Current in blacklist: ${currentInBlacklist}`);
        
            if (currentInBlacklist) {
                // If the album is already in the blacklist, remove it
                if (!confirm('Are you sure you want to remove this album from your blacklist?')) {
                    return;
                }
        
                fetch('/collection/remove_album_from_blacklist/', {
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
                        // alert(data.message);

                        const blacklistHeader = document.querySelector('.blacklist-header p');
                        if (blacklistHeader) {
                            albumItem.remove();
                        
                            const currentCount = parseInt(blacklistHeader.textContent.match(/\d+/)[0], 10);
                            if (currentCount > 1) {
                                blacklistHeader.textContent = `You have added ${currentCount - 1} album(s) to your blacklist.`;
                            } else {
                                blacklistHeader.textContent = 'Your blacklist is empty.';
                            }
                        }
                        
                        updateAlbumState(albumItem, false); // Update the state to reflect removal
                    } else {
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
            } else {
                // If the album is not in the blacklist, add it
                const albumName = albumItem.dataset.albumName;
                const albumType = albumItem.dataset.albumType;
                const releaseDate = albumItem.dataset.releaseDate;
                const imageUrl = albumItem.dataset.imageUrl;
                const artistName = albumItem.dataset.artistName;

                // proof first and eventually remove from wishlist/collection
                const promises = [];

                if (currentInWishlist) {
                    promises.push(fetch('/collection/remove_album_from_wishlist/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                        },
                        body: JSON.stringify({ album_id: albumId }),
                    }));
                }
        
                if (currentInCollection) {
                    promises.push(fetch('/collection/remove_album_from_collection/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                        },
                        body: JSON.stringify({ album_id: albumId }),
                    }));
                }
        
                // wait until done
                Promise.all(promises)
                .then(() => {
                    return fetch('/collection/add_album_to_blacklist/', {
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
                    });
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
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
