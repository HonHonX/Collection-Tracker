document.addEventListener('DOMContentLoaded', function () {
    if (window.location.pathname.includes('search') || window.location.pathname.includes('home')) {
        updateProgressBars();
    }

    document.querySelectorAll('.album-item').forEach(albumItem => {
        // Collection control icon & state
        const controlIconCollection = albumItem.querySelector('#collection-control-icon');
        const controlIconWishlist = albumItem.querySelector('#wishlist-control-icon');
        const controlIconBlacklist = albumItem.querySelector('#blacklist-control-icon');

        setupControlIcon(albumItem, controlIconCollection, 'collection', "/static/icons/add.svg", "/static/icons/remove.svg", "Add to collection", "Already added to collection");
        setupControlIcon(albumItem, controlIconWishlist, 'wishlist', "/static/icons/wishlist_add.svg", "/static/icons/wishlist_remove.svg", "Add to wishlist", "Already added to wishlist");
        setupControlIcon(albumItem, controlIconBlacklist, 'blacklist', "/static/icons/blacklist_add.svg", "/static/icons/blacklist_remove.svg", "Add to blacklist", "Already added to blacklist");

        // Update background color based on the album's state
        updateAlbumBackgroundColor(albumItem);
    });

    function setupControlIcon(albumItem, controlIcon, listType, addIcon, removeIcon, altAdd, altRemove) {
        if (controlIcon) {
            updateAlbumState(albumItem.dataset[`in${capitalize(listType)}`] === 'true', controlIcon, addIcon, removeIcon, altAdd, altRemove);
            controlIcon.addEventListener('click', () => handleAlbumClick(albumItem, listType, controlIcon, addIcon, removeIcon, altAdd, altRemove));
        }
    }

    // Update the state of album icons based on its list status (in collection, wishlist, or blacklist)
    function updateAlbumState(isInList, controlIcon, addIcon, removeIcon, altAdd, altRemove) {
        if (controlIcon) {
            if (isInList) {
                controlIcon.alt = altRemove;
                controlIcon.src = removeIcon;
            } else {
                controlIcon.alt = altAdd;
                controlIcon.src = addIcon;
            }
        }
    }

    // Update the background color of an album item based on the state of the album
    function updateAlbumBackgroundColor(albumItem) {
        const inCollection = albumItem.dataset.inCollection === 'true';
        const inWishlist = albumItem.dataset.inWishlist === 'true';
        const inBlacklist = albumItem.dataset.inBlacklist === 'true';

        albumItem.classList.remove('disabled');

        if (inBlacklist) {
            albumItem.style.backgroundColor = 'var(--neutral70)';
            albumItem.classList.add('disabled');
        }
        else if (inWishlist && inCollection) {
            albumItem.style.backgroundColor = 'var(--accentVariantA100)';
        } else if (inWishlist) {
            albumItem.style.backgroundColor = 'var(--accentVariantB100)';
        } else if (inCollection) {
            albumItem.style.backgroundColor = 'var(--accent100)';
        } else {
            albumItem.style.backgroundColor = 'var(--neutral100)';
        }

        // Disable/enable control icons based on blacklist status
        toggleControlIcons(albumItem, inBlacklist);
    }

    function toggleControlIcons(albumItem, disable) {
        const controlIconCollection = albumItem.querySelector('#collection-control-icon');
        const controlIconWishlist = albumItem.querySelector('#wishlist-control-icon');
    
        if (controlIconCollection) {
            controlIconCollection.disabled = disable;
        } else {
            console.log('Collection control icon not found');
        }
    
        if (controlIconWishlist) {
            controlIconWishlist.disabled = disable;
        } else {
            console.log('Wishlist control icon not found');
        }
    }

    // Handle the click event for adding/removing albums from collection, wishlist, or blacklist
    async function handleAlbumClick(albumItem, listType, iconElement, addIcon, removeIcon, altAdd, altRemove) {
        const isInList = albumItem.dataset[`in${capitalize(listType)}`] === 'true';
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const albumId = albumItem.dataset.albumId;
        const albumName = albumItem.dataset.albumName;
        const albumType = albumItem.dataset.albumType;
        const releaseDate = albumItem.dataset.releaseDate;
        const imageUrl = albumItem.dataset.imageUrl;

        const action = isInList ? 'remove' : 'add';
        const url = `/manage_album/${listType}/${action}/`;

        // Get the current page URL path
        const currentPage = window.location.pathname;

        // Check, what site is
        const isCollectionPage = currentPage.includes('collection');
        const isWishlistPage = currentPage.includes('wishlist');
        const isBlacklistPage = currentPage.includes('blacklist');

        if (isInList && !confirm(`Are you sure you want to remove this album from your ${listType}?`)) {
            return;
        }

        try {
            const response = await fetch(url, {
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
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to update the album status');
            }

            const data = await response.json();

            if (data.success) {
                const newState = action === 'add';
                document.querySelectorAll(`.album-item[data-album-id="${albumId}"]`).forEach(item => {
                    item.dataset[`in${capitalize(listType)}`] = newState.toString();
                    const controlIcon = item.querySelector(`#${listType}-control-icon`);
                    updateAlbumState(newState, controlIcon, addIcon, removeIcon, altAdd, altRemove);
                    updateAlbumBackgroundColor(item);

                    // If adding to blacklist, remove from collection and wishlist
                    if (listType === 'blacklist' && newState) {
                        removeFromOtherLists(item, 'collection', csrfToken);
                        removeFromOtherLists(item, 'wishlist', csrfToken);
                    }
                });

                if (window.location.pathname.includes('search') || window.location.pathname.includes('home')) {
                    updateProgressBars();
                }

            } else {
                alert(data.error || data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    }

    async function removeFromOtherLists(albumItem, listType, csrfToken) {
        if (albumItem.dataset[`in${capitalize(listType)}`] === 'true') {
            albumItem.dataset[`in${capitalize(listType)}`] = 'false';
            const controlIcon = albumItem.querySelector(`#${listType}-control-icon`);
            const addIcon = listType === 'collection' ? "/static/icons/add.svg" : "/static/icons/wishlist_add.svg";
            const removeIcon = listType === 'collection' ? "/static/icons/remove.svg" : "/static/icons/wishlist_remove.svg";
            const altAdd = listType === 'collection' ? "Add to collection" : "Add to wishlist";
            const altRemove = listType === 'collection' ? "Already added to collection" : "Already added to wishlist";

            const albumId = albumItem.dataset.albumId;
            const albumName = albumItem.dataset.albumName;
            const albumType = albumItem.dataset.albumType;
            const releaseDate = albumItem.dataset.releaseDate;
            const imageUrl = albumItem.dataset.imageUrl;

            const url = `/manage_album/${listType}/remove/`;

            try {
                const response = await fetch(url, {
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
                    }),
                });

                if (!response.ok) {
                    throw new Error(`Failed to remove album from ${listType}`);
                }

                const data = await response.json();

                if (!data.success) {
                    alert(data.error || data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }

            updateAlbumState(false, controlIcon, addIcon, removeIcon, altAdd, altRemove);
        }
    }

    // Update progress bars and counters after changes
    function updateProgressBars() {
        document.querySelectorAll('.artist-card, .artist-detail').forEach(artistElement => {
            const totalAlbumsElement = artistElement.querySelector(".total-albums");
            if (!totalAlbumsElement) {
                console.warn("Total albums element not found for artist element", artistElement);
                return;
            }

            const totalAlbums = parseInt(totalAlbumsElement.textContent, 10);

            let collectionCount = 0;
            let wishlistCount = 0;
            let collectionAndWishlistCount = 0;
            let blacklistCount = 0;

            // Count albums based on data attributes, excluding blacklisted ones
            var albumItems = artistElement.querySelectorAll('.album-item');
            if (window.location.pathname.includes('search')) {
                albumItems = document.querySelectorAll('.album-item');
            }
            albumItems.forEach(albumItem => {
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
            updateCounter(artistElement, ".collection-counter", collectionCount);
            updateCounter(artistElement, ".collection-and-wishlist-counter", collectionAndWishlistCount);
            updateCounter(artistElement, ".wishlist-counter", wishlistCount);
            updateCounter(artistElement, ".blacklist-counter", blacklistCount);

            // Calculate the progress based on the remaining albums (excluding blacklisted albums)
            const totalNonBlacklistedAlbums = totalAlbums - blacklistCount;  // Exclude blacklisted albums from the total

            // If there are no non-blacklisted albums, set progress to 0% to avoid division by 0
            var collectionProgress = totalNonBlacklistedAlbums > 0 ? (collectionCount / totalNonBlacklistedAlbums) * 100 : 0;
            const wishlistProgress = totalNonBlacklistedAlbums > 0 ? (wishlistCount / totalNonBlacklistedAlbums) * 100 : 0;
            const collectionAndWishlistProgress = totalNonBlacklistedAlbums > 0 ? (collectionAndWishlistCount / totalNonBlacklistedAlbums) * 100 : 0;

            // Update progress bars
            updateProgressBar(artistElement, ".collection-progress", collectionProgress);
            updateProgressBar(artistElement, ".collection-and-wishlist-progress", collectionAndWishlistProgress);
            updateProgressBar(artistElement, ".wishlist-progress", wishlistProgress);

            // Update percentage
            collectionProgress = Math.round(collectionProgress + collectionAndWishlistProgress);
            artistElement.querySelector(".collection-percentage").textContent = `${collectionProgress}%`;
        });
    }

    function updateCounter(element, selector, count) {
        const counter = element.querySelector(selector);
        if (counter) {
            counter.textContent = count;
        }
    }

    function updateProgressBar(element, selector, progress) {
        const progressBar = element.querySelector(selector);
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }

    // Capitalize the first letter of a string (e.g., 'collection' -> 'Collection')
    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
});
