document.addEventListener('DOMContentLoaded', () => {
    const sortAscIcon = "/static/icons/sort-asc.svg";
    const sortDescIcon = "/static/icons/sort-desc.svg";

    const sortCriteria = document.getElementById("sort-criteria");
    const sortToggle = document.getElementById("sort-toggle");
    const albumGrid = document.querySelector(".album-grid");

    function sortAlbums() {
        const criteria = sortCriteria.value;
        const order = sortToggle.dataset.sortOrder;
        const albums = Array.from(albumGrid.getElementsByClassName("album-item"));

        albums.sort((a, b) => {
            let valueA = a.dataset[criteria] || ''; // Fallback for missing attributes
            let valueB = b.dataset[criteria] || ''; // Fallback for missing attributes

            if (criteria === 'release_date') {
                // Parse dates for sorting
                valueA = new Date(valueA).getTime() || 0;
                valueB = new Date(valueB).getTime() || 0;
            } else {
                // Ensure `toLowerCase` is called only on strings
                valueA = valueA.toString().toLowerCase();
                valueB = valueB.toString().toLowerCase();
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

    // Toggle sort order and re-sort
    sortToggle.addEventListener("click", () => {
        const currentOrder = sortToggle.dataset.sortOrder;
        const newOrder = currentOrder === "asc" ? "desc" : "asc";
        sortToggle.dataset.sortOrder = newOrder;

        // Change the icon based on the new order (ascending or descending)
        sortToggle.src = newOrder === "asc" ? sortAscIcon : sortDescIcon;

        sortAlbums();
    });

    // Re-sort when the criteria changes
    sortCriteria.addEventListener("change", sortAlbums);
});
