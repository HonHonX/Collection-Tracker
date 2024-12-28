document.addEventListener('DOMContentLoaded', function() {
    // Home Button
    var homeUrl = document.getElementById('home-button').getAttribute('home-url');
    document.getElementById('home-button').addEventListener('click', function() {
        window.location.href = "/index";
    });

    // Search Button
    document.addEventListener('click', function(event) {
        const searchBar = document.querySelector('.searchbar');
        const searchButton = document.getElementById('search-button');

        if (!searchButton.contains(event.target) && !searchBar.contains(event.target)) {
            searchBar.classList.remove('visible');
        } else if (searchButton.contains(event.target)) {
            searchBar.classList.toggle('visible');
        }
    });

    // Collection Button
    var collectionUrl = document.getElementById('collection-button').getAttribute('data-collection-url');
    document.getElementById('collection-button').addEventListener('click', function() {
        window.location.href = collectionUrl;
    });

    // Wishlist Button (Placeholder)
    document.getElementById('wishlist-button').addEventListener('click', function() {
        console.log("Wishlist clicked!");
    });

    // Settings Button (Placeholder)
    document.getElementById('settings-button').addEventListener('click', function() {
        console.log("Settings clicked!");
    });
});
