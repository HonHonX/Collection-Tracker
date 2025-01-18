document.getElementById('edit-discogs-button').addEventListener('click', function() {
    var discogsDiv = document.getElementById('discogs-div');
    var tracklistDiv = document.getElementById('album-tracklist');
    var priceStatsDiv = document.getElementById('price-stats');
    if (discogsDiv.style.display === 'none') {
        discogsDiv.style.display = 'block';
        if (tracklistDiv) tracklistDiv.style.display = 'none';
        if (priceStatsDiv) priceStatsDiv.style.display = 'none';
    } else {
        discogsDiv.style.display = 'none';
        if (tracklistDiv) tracklistDiv.style.display = 'block';
        if (priceStatsDiv) priceStatsDiv.style.display = 'block';
    }
});
