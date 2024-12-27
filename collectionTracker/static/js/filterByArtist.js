document.addEventListener('DOMContentLoaded', function() {
    const artistFilter = document.getElementById('artist-filter');
    const albumItems = document.querySelectorAll('.album-item');

    artistFilter.addEventListener('change', function() {
        const selectedArtist = artistFilter.value.toLowerCase();

        albumItems.forEach(function(item) {
            const artist = item.getAttribute('data-artist').toLowerCase();

            if (selectedArtist === '' || artist.includes(selectedArtist)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });
});

