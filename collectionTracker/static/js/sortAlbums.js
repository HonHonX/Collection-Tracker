document.addEventListener('DOMContentLoaded', () => {
    const sortCriteria = document.getElementById('sort-criteria');
    const sortOrder = document.getElementById('sort-order');
    const albumGrid = document.querySelector('.album-grid');

    function sortAlbums() {
        const criteria = sortCriteria.value;
        const order = sortOrder.value;
        
        // Convert NodeList to Array for sorting
        const albums = Array.from(albumGrid.children);

        albums.sort((a, b) => {
            let valueA = a.dataset[criteria].toLowerCase();
            let valueB = b.dataset[criteria].toLowerCase();

            // Handle numeric sorting (e.g., release date)
            if (criteria === 'release_date') {
                valueA = new Date(valueA);
                valueB = new Date(valueB);
            }

            if (order === 'asc') {
                return valueA > valueB ? 1 : -1;
            } else {
                return valueA < valueB ? 1 : -1;
            }
        });

        // Clear and re-append sorted albums
        albumGrid.innerHTML = '';
        albums.forEach(album => albumGrid.appendChild(album));
    }

    // Add event listeners
    sortCriteria.addEventListener('change', sortAlbums);
    sortOrder.addEventListener('change', sortAlbums);
});
