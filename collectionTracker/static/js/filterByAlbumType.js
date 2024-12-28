document.addEventListener('DOMContentLoaded', function() {
    const albumTypeFilter = document.getElementById('album-type-filter');
    const albumItems = document.querySelectorAll('.album-item');

    // Function to filter by album type
    function filterByAlbumType() {
        const selectedAlbumType = albumTypeFilter ? albumTypeFilter.value.toLowerCase() : '';

        albumItems.forEach(function(item) {
            const albumType = item.getAttribute('data-album-type').toLowerCase();

            // Show item if it matches the selected album type
            if (selectedAlbumType === '' || albumType === selectedAlbumType) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    // Add event listener for the album type filter
    if (albumTypeFilter) {
        albumTypeFilter.addEventListener('change', filterByAlbumType);
    }
});
