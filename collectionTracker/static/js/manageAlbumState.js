document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.album-item').forEach(albumItem => {
        // Collection control icon & state
        const controlIconCollection = albumItem.querySelector('#control-icon');
        const controlIconWishlist = albumItem.querySelector('#wishlist-control-icon');
        const controlIconBlacklist = albumItem.querySelector('#blacklist-control-icon');

        // Initialize the album state based on list status
        updateAlbumState(albumItem.dataset.inCollection === 'true', controlIconCollection, "/static/icons/add.svg", "/static/icons/remove.svg", "Add to collection", "Already added to collection");
        updateAlbumState(albumItem.dataset.inWishlist === 'true', controlIconWishlist, "/static/icons/wishlist_add.svg", "/static/icons/wishlist_remove.svg", "Add to wishlist", "Already added to wishlist");
        updateAlbumState(albumItem.dataset.inBlacklist === 'true', controlIconBlacklist, "/static/icons/blacklist_add.svg", "/static/icons/blacklist_remove.svg", "Add to blacklist", "Already added to blacklist");

        // Update background color based on the album's state
        updateAlbumBackgroundColor(albumItem);

        // Set event listeners for control icons
        controlIconCollection.addEventListener('click', () => handleAlbumClick(albumItem, 'collection', controlIconCollection, "/static/icons/add.svg", "/static/icons/remove.svg", "Add to collection", "Already added to collection"));
        controlIconWishlist.addEventListener('click', () => handleAlbumClick(albumItem, 'wishlist', controlIconWishlist, "/static/icons/wishlist_add.svg", "/static/icons/wishlist_remove.svg", "Add to wishlist", "Already added to wishlist"));
        controlIconBlacklist.addEventListener('click', () => handleAlbumClick(albumItem, 'blacklist', controlIconBlacklist, "/static/icons/blacklist_add.svg", "/static/icons/blacklist_remove.svg", "Add to blacklist", "Already added to blacklist"));
    });

    function updateAlbumState(isInList, controlIcon, addIcon, removeIcon, altAdd, altRemove) {
        if (isInList) {
            controlIcon.alt = altRemove;
            controlIcon.src = removeIcon;
        } else {
            controlIcon.alt = altAdd;
            controlIcon.src = addIcon;
        }
    }

    function updateAlbumBackgroundColor(albumItem) {
        const inCollection = albumItem.dataset.inCollection === 'true';
        const inWishlist = albumItem.dataset.inWishlist === 'true';
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

    function handleAlbumClick(albumItem, listType, iconElement, addIcon, removeIcon, altAdd, altRemove) {
        const isInList = albumItem.dataset[`in${capitalize(listType)}`] === 'true';
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const albumId = albumItem.dataset.albumId;
        const albumName = albumItem.dataset.albumName;
        const albumType = albumItem.dataset.albumType;
        const releaseDate = albumItem.dataset.releaseDate;
        const imageUrl = albumItem.dataset.imageUrl;
        const artistName = albumItem.dataset.artistName;

        const action = isInList ? 'remove' : 'add';
        const url = `/collection/manage_album/${listType}/${action}/`;

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
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const newState = action === 'add';
                albumItem.dataset[`in${capitalize(listType)}`] = newState.toString();
                updateAlbumState(newState, iconElement, addIcon, removeIcon, altAdd, altRemove);
                updateAlbumBackgroundColor(albumItem);
            } else {
                alert(data.error || data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }

    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
});
