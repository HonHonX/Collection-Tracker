document.addEventListener('DOMContentLoaded', function () {
    // Update progress bars on page load to reflect initial state
    if (window.location.pathname.includes('search')) {
        updateProgressBars();
    }

    document.querySelectorAll('.album-item').forEach(albumItem => {
        // Collection control icon & state
        const controlIconCollection = albumItem.querySelector('#control-icon');
        const controlIconWishlist = albumItem.querySelector('#wishlist-control-icon');
        const controlIconBlacklist = albumItem.querySelector('#blacklist-control-icon');

        // Ensure that the control icon exists before using it
        if (controlIconCollection) {
            updateAlbumState(albumItem.dataset.inCollection === 'true', controlIconCollection, "/static/icons/add.svg", "/static/icons/remove.svg", "Add to collection", "Already added to collection");
            controlIconCollection.addEventListener('click', () => handleAlbumClick(albumItem, 'collection', controlIconCollection, "/static/icons/add.svg", "/static/icons/remove.svg", "Add to collection", "Already added to collection", controlIconCollection,  controlIconWishlist));
        }

        if (controlIconWishlist) {
            updateAlbumState(albumItem.dataset.inWishlist === 'true', controlIconWishlist, "/static/icons/wishlist_add.svg", "/static/icons/wishlist_remove.svg", "Add to wishlist", "Already added to wishlist");
            controlIconWishlist.addEventListener('click', () => handleAlbumClick(albumItem, 'wishlist', controlIconWishlist, "/static/icons/wishlist_add.svg", "/static/icons/wishlist_remove.svg", "Add to wishlist", "Already added to wishlist", controlIconCollection,  controlIconWishlist));
        }

        if (controlIconBlacklist) {
            updateAlbumState(albumItem.dataset.inBlacklist === 'true', controlIconBlacklist, "/static/icons/blacklist_add.svg", "/static/icons/blacklist_remove.svg", "Add to blacklist", "Already added to blacklist");
            controlIconBlacklist.addEventListener('click', () => handleAlbumClick(albumItem, 'blacklist', controlIconBlacklist, "/static/icons/blacklist_add.svg", "/static/icons/blacklist_remove.svg", "Add to blacklist", "Already added to blacklist", controlIconCollection,  controlIconWishlist));
        }

        // Update background color based on the album's state
        updateAlbumBackgroundColor(albumItem);

    });

    // Update the state of album icons based on its list status (in collection, wishlist, or blacklist)
    function updateAlbumState(isInList, controlIcon, addIcon, removeIcon, altAdd, altRemove) {
        if (isInList) {
            controlIcon.alt = altRemove;
            controlIcon.src = removeIcon;
        } else {
            controlIcon.alt = altAdd;
            controlIcon.src = addIcon;
        }
    }

    // Update the background color of an album item based on the state of the album
    function updateAlbumBackgroundColor(albumItem) {
        const inCollection = albumItem.dataset.inCollection === 'true';
        const inWishlist = albumItem.dataset.inWishlist === 'true';
        const inBlacklist = albumItem.dataset.inBlacklist === 'true';

        albumItem.classList.remove('disabled');

        if (inWishlist && inCollection) {
            albumItem.style.backgroundColor = 'var(--accentVariantA100)';
        } else if (inWishlist) {
            albumItem.style.backgroundColor = 'var(--accentVariantB100)';
        } else if (inCollection) {
            albumItem.style.backgroundColor = 'var(--accent100)';
        } else if (inBlacklist) {
            albumItem.style.backgroundColor = 'var(--neutral70)';
            albumItem.classList.add('disabled');
        } else {
            albumItem.style.backgroundColor = 'var(--neutral100)';
        }
    }

    // Handle the click event for adding/removing albums from collection, wishlist, or blacklist
    function handleAlbumClick(albumItem, listType, iconElement, addIcon, removeIcon, altAdd, altRemove, controlIconCollection, controlIconWishlist) {
        const isInList = albumItem.dataset[`in${capitalize(listType)}`] === 'true';
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const albumId = albumItem.dataset.albumId;
        const albumName = albumItem.dataset.albumName;
        const albumType = albumItem.dataset.albumType;
        const releaseDate = albumItem.dataset.releaseDate;
        const imageUrl = albumItem.dataset.imageUrl;
        const artistName = albumItem.dataset.artistName;
        const artistId = albumItem.dataset.artistId;
        const artistPhotoUrl = albumItem.dataset.artistPhotoUrl;
        const artistGenres = albumItem.dataset.artistGenres;
        const artistPopularity = albumItem.dataset.artistPopularity;

        console.log({
            artist_photo_url: albumItem.dataset.artistPhotoUrl,
            artist_genres: albumItem.dataset.artistGenres,
            artist_popularity: albumItem.dataset.artistPopularity,
        });
    
        const action = isInList ? 'remove' : 'add';
        const url = `/collection/manage_album/${listType}/${action}/`;
    
        // Get the current page URL path
        const currentPage = window.location.pathname; 
        const collectionType = (currentPage.match(/\/collection\/([^\/]+)-overview/))?.[1];
    
        // Check, what site is
        const isCollectionPage = currentPage.includes('overview');
        const isWishlistPage = currentPage.includes('wishlist');
        const isBlacklistPage = currentPage.includes('blacklist');
    
        if (isInList && !confirm(`Are you sure you want to remove this album from your ${listType}?`)) {
            return;
        }
    
        fetch(url, {
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
                artist_id: artistId,
                artist_photo_url: artistPhotoUrl,
                artist_genres: artistGenres,
                artist_popularity: artistPopularity,
            }),
        })
        .then(response => {
            if (!response.ok) {
                // If response is not okay, reject the promise with an error message
                throw new Error('Failed to update the album status');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const newState = action === 'add';
                albumItem.dataset[`in${capitalize(listType)}`] = newState.toString();
    
                // Handle blacklist actions
                if (listType == 'blacklist' && action === 'add') {
                    // Remove the album from the collection if it's in there
                    if (albumItem.dataset.inCollection === 'true') {
                        albumItem.dataset.inCollection = 'false';
                        updateAlbumState(false, controlIconCollection, "/static/icons/add.svg", "/static/icons/remove.svg", "Add to collection", "Already added to collection");
    
                        // Remove from collection in the backend
                        fetch('/collection/manage_album/collection/remove/', {
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
                                artist_id: artistId,
                                artist_photo_url: artistPhotoUrl,
                                artist_genres: artistGenres,
                                artist_popularity: artistPopularity,
                            }),
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred while removing from collection.');
                        });
                    }
    
                    // Remove from wishlist in the backend
                    if (albumItem.dataset.inWishlist === 'true') {
                        albumItem.dataset.inWishlist = 'false';
                        updateAlbumState(false, controlIconWishlist, "/static/icons/wishlist_add.svg", "/static/icons/wishlist_remove.svg", "Add to wishlist", "Already added to wishlist");
    
                        fetch('/collection/manage_album/wishlist/remove/', {
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
                                artist_id: artistId,
                                artist_photo_url: artistPhotoUrl,
                                artist_genres: artistGenres,
                                artist_popularity: artistPopularity,
                            }),
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred while removing from wishlist.');
                        });
                    }
                }

                const collectionHeader = document.querySelector('.collection-header p');
                if (collectionHeader) {

                    var currentCount = parseInt(collectionHeader.textContent.match(/\d+/)[0], 10);
                
                    if ((listType == 'collection' && isCollectionPage) || (listType == 'wishlist' && isWishlistPage) || (listType == 'blacklist' && isBlacklistPage)) {
                        if (action === 'add') {
                            currentCount += 1;
                        }
                        else {
                            albumItem.remove();
                            currentCount -= 1;
                        }
                    }                
                    collectionHeader.textContent = `You have ${currentCount} album(s) in your ${collectionType}.`;
                }
    
                // Update album state
                updateAlbumState(newState, iconElement, addIcon, removeIcon, altAdd, altRemove);
                updateAlbumBackgroundColor(albumItem);
    
                // Dynamically update progress bars and counters
                if (window.location.pathname.includes('search')) {
                    updateProgressBars();
                }
            } else {
                alert(data.error || data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }
    

    // Update progress bars and counters after changes
    function updateProgressBars() {
        const totalAlbums = parseInt(document.getElementById("total-albums").textContent, 10);
        let collectionCount = 0;
        let wishlistCount = 0;
        let collectionAndWishlistCount = 0;
        let blacklistCount = 0;
    
        // Count albums based on data attributes, excluding blacklisted ones
        document.querySelectorAll('.album-item').forEach(albumItem => {
            const inCollection = albumItem.dataset.inCollection === 'true';
            const inWishlist = albumItem.dataset.inWishlist === 'true';
            const inBlacklist = albumItem.dataset.inBlacklist === 'true';
    
            // Skip blacklisted albums from the progress calculation
            if (inBlacklist) {
                blacklistCount++;
            }
    
            // If the album is in both the collection and wishlist, count it towards "collection and wishlist"
            if (inCollection && inWishlist) {
                collectionAndWishlistCount++;
                collectionCount--;
                wishlistCount--;
            }
    
            // Count albums in the collection (if they are not blacklisted)
            if (inCollection) {
                collectionCount++;
            }
    
            // Count albums in the wishlist (if they are not blacklisted)
            if (inWishlist) {
                wishlistCount++;
            }
        });
    
        // Update counters
        document.getElementById("collection-counter").textContent = collectionCount;
        document.getElementById("collection-and-wishlist-counter").textContent = collectionAndWishlistCount;
        document.getElementById("wishlist-counter").textContent = wishlistCount;
        document.getElementById("blacklist-counter").textContent = blacklistCount;
    
        // Calculate the progress based on the remaining albums (excluding blacklisted albums)
        const totalNonBlacklistedAlbums = totalAlbums - blacklistCount;  // Exclude blacklisted albums from the total
    
        // If there are no non-blacklisted albums, set progress to 0% to avoid division by 0
        var collectionProgress = totalNonBlacklistedAlbums > 0 ? (collectionCount / totalNonBlacklistedAlbums) * 100 : 0;
        const wishlistProgress = totalNonBlacklistedAlbums > 0 ? (wishlistCount / totalNonBlacklistedAlbums) * 100 : 0;
        const collectionAndWishlistProgress = totalNonBlacklistedAlbums > 0 ? (collectionAndWishlistCount / totalNonBlacklistedAlbums) * 100 : 0;
        const blacklistProgress = totalNonBlacklistedAlbums > 0 ? (blacklistCount / totalNonBlacklistedAlbums) * 100 : 0;
    
        // Update progress bars
        document.getElementById("collection-progress").style.width = `${collectionProgress}%`;
        document.getElementById("collection-and-wishlist-progress").style.width = `${collectionAndWishlistProgress}%`;
        document.getElementById("wishlist-progress").style.width = `${wishlistProgress}%`;

        //Update percentage
        collectionProgress = Math.round(collectionProgress+collectionAndWishlistProgress);
        document.getElementById("collection-percentage").textContent = `${collectionProgress}%`;
    }    

    // Capitalize the first letter of a string (e.g., 'collection' -> 'Collection')
    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
});
