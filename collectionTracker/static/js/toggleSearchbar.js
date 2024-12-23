document.addEventListener('click', function (event) {
    const searchBar = document.querySelector('.input-group');
    if (!searchBar.contains(event.target) && searchBar.classList.contains('visible')) {
        searchBar.classList.remove('visible');
    }
});
