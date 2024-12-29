document.addEventListener('DOMContentLoaded', function () {
    // Loop through each album and update its state (in wishlist)
    document.querySelectorAll('.album-item').forEach(albumItem => {
        const inWishlist = albumItem.dataset.inWishlist === 'true'; // Check initial state of the album
        const controlIcon = albumItem.querySelector('#wishlist-control-icon');

        // console.log("Initial inWishlist state:", inWishlist);

        // Initialize the state based on whether the album is in the wishlist or not
        updateAlbumState(albumItem, inWishlist);

        // Attach the correct event listener based on the album's state
        setControlIconClickListener(albumItem, controlIcon, inWishlist);
    });

    // Function to update the UI based on whether the album is in the wishlist
    function updateAlbumState(albumItem, inWishlist) {
        const controlIcon = albumItem.querySelector('#wishlist-control-icon');

        // // Debugging log
        // console.log(`Updating state for album: ${albumItem.dataset.albumId}, In wishlist: ${inWishlist}`);

        if (inWishlist) {
            albumItem.dataset.inWishlist = 'true';
            controlIcon.classList.add('wanted');
            controlIcon.alt = "Already added";
            controlIcon.src = "/static/icons/wishlist_remove.svg"; // Change the icon to 'remove'
        } else {
            albumItem.dataset.inWishlist = 'false';
            controlIcon.classList.remove('wanted');
            controlIcon.alt = "Add to wishlist";
            controlIcon.src = "/static/icons/wishlist_add.svg"; // Reset to 'add' icon
        }

        // Update the background color based on the current state
        updateAlbumBackgroundColor(albumItem); 
    }

    // Function to update the background color
    function updateAlbumBackgroundColor(albumItem) {
        const inWishlist = albumItem.dataset.inWishlist === 'true';
        const inCollection = albumItem.dataset.inCollection === 'true';

        // console.log("About to update the album bg - in Wishlist:", inWishlist)
        // console.log("About to update the album bg - in Collection:", inCollection)

        if (inWishlist && inCollection) {
            albumItem.style.backgroundColor = 'var(--accentVariantA100)'; // Background if in both
        } else if (inWishlist) {
            albumItem.style.backgroundColor = 'var(--accentVariantB100)'; // Wishlist background
        } else if (inCollection) {
            albumItem.style.backgroundColor = 'var(--accent100)'; // Collection background
        } else {
            albumItem.style.backgroundColor = 'var(--neutral100)'; // Default background
        }
    }

    // Function to set the appropriate event listener for the control icon
    function setControlIconClickListener(albumItem, controlIcon, inWishlist) {
        // Remove any existing event listener to avoid duplicates
        controlIcon.removeEventListener('click', handleAlbumClick);

        inWishlist = albumItem.dataset.inWishlist === 'true'; 

        // Attach the correct event listener based on the album's current inWishlist state
        controlIcon.addEventListener('click', handleAlbumClick);

        function handleAlbumClick() {
            const albumId = albumItem.dataset.albumId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
            // Dynamically fetch the current state
            const currentInWishlist= albumItem.dataset.inWishlist === 'true';
        
            // console.log(`Clicked on album: ${albumId}. Current in wishlist: ${currentInWishlist}`);
        
            if (currentInWishlist) {
                // If the album is already in the wishlist, remove it
                if (!confirm('Are you sure you want to remove this album from your wishlist?')) {
                    return;
                }
        
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
                        // alert(data.message);

                        const wishlistHeader = document.querySelector('.wishlist-header p');
                        if (wishlistHeader) {
                            albumItem.remove();
                        
                            const currentCount = parseInt(wishlistHeader.textContent.match(/\d+/)[0], 10);
                            if (currentCount > 1) {
                                wishlistHeader.textContent = `You have added ${currentCount - 1} album(s) to your wishlist.`;
                            } else {
                                wishlistHeader.textContent = 'Your wishlist is empty.';
                            }
                        }
                        
                        updateAlbumState(albumItem, false); // Update the state to reflect removal
                    } else {
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
            } else {
                // If the album is not in the wishlist, add it
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
                .then(response => {
                    console.log(response.status, response.statusText); // Logs HTTP status
                    return response.text(); // Read raw response as text
                })
                .then(text => {
                    console.log('Response body:', text); // Log raw response
                    const data = JSON.parse(text); // Parse if it's JSON
                    if (data.success) {
                        // alert(data.message);
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
