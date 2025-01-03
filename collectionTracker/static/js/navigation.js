document.addEventListener('DOMContentLoaded', function() {
    // Home Button
    var homeButton = document.getElementById('home-button');
    if (homeButton) {
        var homeUrl = homeButton.getAttribute('data-home-url');
        if (homeUrl) {
            homeButton.addEventListener('click', function() {
                window.location.href = homeUrl;
            });
        } else {
            console.error('Home URL is not defined');
        }
    }

    // Profile Button
    var profileButton = document.getElementById('profile-button');
    if (profileButton) {
        var profileUrl = profileButton.getAttribute('data-profile-url');
        profileButton.addEventListener('click', function() {
            window.location.href = profileUrl;
        });
    }

    // Search Button
    document.addEventListener('click', function(event) {
        const searchBar = document.querySelector('.searchbar');
        const searchButton = document.getElementById('search-button');

        if (searchButton && searchBar) {
            if (!searchButton.contains(event.target) && !searchBar.contains(event.target)) {
                searchBar.classList.remove('visible');
            } else if (searchButton.contains(event.target)) {
                searchBar.classList.toggle('visible');
            }
        }
    });

    // Collection Button
    var collectionButton = document.getElementById('collection-button');
    if (collectionButton) {
        var collectionUrl = collectionButton.getAttribute('data-collection-url');
        collectionButton.addEventListener('click', function() {
            window.location.href = collectionUrl;
        });
    }

    // Wishlist Button
    var wishlistButton = document.getElementById('wishlist-button');
    if (wishlistButton) {
        var wishlistUrl = wishlistButton.getAttribute('data-wishlist-url');
        wishlistButton.addEventListener('click', function() {
            window.location.href = wishlistUrl;
        });
    }

    // Blacklist Button
    var blacklistButton = document.getElementById('blacklist-button');
    if (blacklistButton) {
        var blacklistUrl = blacklistButton.getAttribute('data-blacklist-url');
        blacklistButton.addEventListener('click', function() {
            window.location.href = blacklistUrl;
        });
    }

    // Statistics Button
    var dashboardButton = document.getElementById('dashboard-button');
    if (dashboardButton) {
        var dashboardUrl = dashboardButton.getAttribute('data-dashboard-url');
        dashboardButton.addEventListener('click', function() {
            window.location.href = dashboardUrl;
        });
    }

    // Friends Button
    var friendsButton = document.getElementById('friends-button');
    if (friendsButton) {
        console.log('Friends button found'); // Debugging line
        var friendsUrl = friendsButton.getAttribute('data-friends-url');
        console.log('Friends URL:', friendsUrl); // Debugging line
        friendsButton.addEventListener('click', function() {
            console.log('Friends button clicked'); // Debugging line
            window.location.href = friendsUrl;
        });
    } else {
        console.log('Friends button not found'); // Debugging line
    }

    // Settings Button
    var settingsButton = document.getElementById('settings-button');
    if (settingsButton) {
        var settingsUrl = settingsButton.getAttribute('data-settings-url');
        settingsButton.addEventListener('click', function() {
            window.location.href = settingsUrl;
        });
    }

    // Mobile Navigation
    const searchIcon = document.getElementById("mobile-search"); // Search icon in the navbar
    const searchBar = document.getElementById("popup-searchbar"); // Popup search bar
    const backdrop = document.getElementById("backdrop"); // Backdrop element
    const body = document.body; // Body to manage scrolling

    if (searchIcon && searchBar && backdrop) {
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
    }
});
