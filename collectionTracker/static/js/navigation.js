document.addEventListener('DOMContentLoaded', function() {

    // Function to handle button clicks and navigation
    function setupNavigation(buttonId, dataUrlAttribute) {
        var button = document.getElementById(buttonId);
        if (button) {
            var url = button.getAttribute(dataUrlAttribute);
            if (url) {
                button.addEventListener('click', function() {
                    window.location.href = url;
                });
            } else {
                console.error(`${buttonId} does not have a ${dataUrlAttribute} defined`);
            }
        } else {
            console.log(`${buttonId} button not found`);
        }
    }

    // Setting up buttons using the function
    setupNavigation('home-button', 'data-home-url');
    setupNavigation('profile-button', 'data-profile-url');
    setupNavigation('collection-button', 'data-collection-url');
    setupNavigation('wishlist-button', 'data-wishlist-url');
    setupNavigation('blacklist-button', 'data-blacklist-url');
    setupNavigation('dashboard-button', 'data-dashboard-url');
    setupNavigation('friends-button', 'data-friends-url');

    // Mobile Navigation setup using the function
    setupNavigation('mobile-home-button', 'data-home-url');
    setupNavigation('mobile-collection-button', 'data-collection-url');
    setupNavigation('mobile-profile-button', 'data-profile-url');
    setupNavigation('mobile-wishlist-button', 'data-wishlist-url');

    
        // Profile Button Click - Toggle Dropdown
        const profileButton = document.getElementById('mobile-profile-button');
        if (profileButton) {
            profileButton.addEventListener('click', function(event) {
                const dropdownMenu = document.getElementById('dropdown-menu');
                
                if (dropdownMenu) {
                    // Toggle dropdown visibility
                    if (dropdownMenu.classList.contains('show')) {
                        dropdownMenu.classList.remove('show');
                    } else {
                        dropdownMenu.classList.add('show'); 
                    }
                }
            });
        }  

    // Mobile Search Bar Toggle
    const searchIcon = document.getElementById("mobile-search"); // Search icon in the navbar
    const searchBar = document.getElementById("popup-searchbar"); // Popup search bar
    const backdrop = document.getElementById("backdrop"); // Backdrop element
    const body = document.body; // Body to manage scrolling

    if (searchIcon && searchBar && backdrop) {
        function showSearchBar() {
            searchBar.classList.add("visible");
            backdrop.classList.add("visible");
            body.classList.add("no-scroll"); // Prevent scrolling
        }

        function hideSearchBar() {
            searchBar.classList.remove("visible");
            backdrop.classList.remove("visible");
            body.classList.remove("no-scroll"); // Restore scrolling
        }

        searchIcon.addEventListener("click", showSearchBar);
        backdrop.addEventListener("click", hideSearchBar);

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && searchBar.classList.contains("visible")) {
                hideSearchBar();
            }
        });
    } else {
        console.error("Search bar or backdrop elements are missing.");
    }

});
