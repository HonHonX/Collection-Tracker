document.addEventListener('DOMContentLoaded', function() {
    const artistFilter = document.getElementById('artist-filter');
    const albumItems = document.querySelectorAll('.album-item');

    artistFilter.addEventListener('change', function() {

        console.log('artistFilter change event fired');
        const selectedArtist = artistFilter.value;

        albumItems.forEach(function(item) {
            const artist = item.getAttribute('data-artist-name');

            if (selectedArtist === '' || artist.includes(selectedArtist)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });
});

  