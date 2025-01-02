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

    // Wishlist Button
    var wishlistUrl = document.getElementById('wishlist-button').getAttribute('data-wishlist-url');
    document.getElementById('wishlist-button').addEventListener('click', function() {
        window.location.href = wishlistUrl;
    });

    // Blacklist Button
    var blacklistUrl = document.getElementById('blacklist-button').getAttribute('data-blacklist-url');
    document.getElementById('blacklist-button').addEventListener('click', function() {
        window.location.href = blacklistUrl;
    });

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
 
    // Settings Button (Placeholder)
    document.getElementById('settings-button').addEventListener('click', function() {
        console.log("Settings clicked!");
    });
});
