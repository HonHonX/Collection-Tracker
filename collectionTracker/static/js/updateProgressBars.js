// Update progress bars and counters after changes
function updateProgressBars() {
    console.log("updateProgressBars called");
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
        const collectionCounter = artistElement.querySelector(".collection-counter");
        if (collectionCounter) {
            collectionCounter.textContent = collectionCount;
        }

        const collectionAndWishlistCounter = artistElement.querySelector(".collection-and-wishlist-counter");
        if (collectionAndWishlistCounter) {
            collectionAndWishlistCounter.textContent = collectionAndWishlistCount;
        }

        const wishlistCounter = artistElement.querySelector(".wishlist-counter");
        if (wishlistCounter) {
            wishlistCounter.textContent = wishlistCount;
        }

        const blacklistCounter = artistElement.querySelector(".blacklist-counter");
        if (blacklistCounter) {
            blacklistCounter.textContent = blacklistCount;
        }

        // Calculate the progress based on the remaining albums (excluding blacklisted albums)
        const totalNonBlacklistedAlbums = totalAlbums - blacklistCount;  // Exclude blacklisted albums from the total
        console.log("totalNonBlacklistedAlbums", totalNonBlacklistedAlbums);

        // If there are no non-blacklisted albums, set progress to 0% to avoid division by 0
        var collectionProgress = totalNonBlacklistedAlbums > 0 ? (collectionCount / totalNonBlacklistedAlbums) * 100 : 0;
        const wishlistProgress = totalNonBlacklistedAlbums > 0 ? (wishlistCount / totalNonBlacklistedAlbums) * 100 : 0;
        const collectionAndWishlistProgress = totalNonBlacklistedAlbums > 0 ? (collectionAndWishlistCount / totalNonBlacklistedAlbums) * 100 : 0;

        // Update progress bars
        artistElement.querySelector(".collection-progress").style.width = `${collectionProgress}%`;
        artistElement.querySelector(".collection-and-wishlist-progress").style.width = `${collectionAndWishlistProgress}%`;
        artistElement.querySelector(".wishlist-progress").style.width = `${wishlistProgress}%`;

        // Update percentage
        collectionProgress = Math.round(collectionProgress + collectionAndWishlistProgress);
        artistElement.querySelector(".collection-percentage").textContent = `${collectionProgress}%`;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    updateProgressBars();

    // Add event listener for icon clicks inside maincontent
    document.querySelectorAll('.icon').forEach(icon => {
        icon.addEventListener('click', function(event) {
            // Simulate a delay for the update to complete
            setTimeout(updateProgressBars, 100);
        });
    });
});
