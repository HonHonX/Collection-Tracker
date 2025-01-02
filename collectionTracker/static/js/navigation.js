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

    // Wishlist Butto
    var wishlistUrl = document.getElementById('wishlist-button').getAttribute('data-wishlist-url');
    document.getElementById('wishlist-button').addEventListener('click', function() {
        window.location.href = wishlistUrl;
    });

    // Settings Button (Placeholder)
    document.getElementById('settings-button').addEventListener('click', function() {
        console.log("Settings clicked!");
    });

    // Mobile Navigation
    const searchIcon = document.getElementById("mobile-search"); // Search icon in the navbar
    const searchBar = document.getElementById("popup-searchbar"); // Popup search bar
    const backdrop = document.getElementById("backdrop"); // Backdrop element
    const body = document.body; // Body to manage scrolling

    // Mobile Search Button
    function showSearchBar() {
        searchBar.classList.add("visible");
        backdrop.classList.add("visible");
        body.classList.add("no-scroll"); // Prevent scrolling
    }

        // Hide the popup search bar
        function hideSearchBar() {
            searchBar.classList.remove("visible");
            backdrop.classList.remove("visible");
            body.classList.remove("no-scroll"); // Restore scrolling
        }

        // Open search bar on click of the search icon
        searchIcon.addEventListener("click", showSearchBar);

        // Close search bar on click of the backdrop
        backdrop.addEventListener("click", hideSearchBar);

        // Close search bar on pressing the Escape key
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && searchBar.classList.contains("visible")) {
                hideSearchBar();
            }
        });
    
});
