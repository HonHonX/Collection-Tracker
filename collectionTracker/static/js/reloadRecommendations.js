document.getElementById('reload-recommendations-icon').addEventListener('click', function() {
    fetch("/reload-recommendations/")
        .then(response => response.json())
        .then(data => {
            // Update the recommended artists section with the new data
            const artistRecommendationDiv = document.querySelector('.artist-recommendation');
            artistRecommendationDiv.innerHTML = '';
            if (data.recommended_artists.length === 0) {
                artistRecommendationDiv.innerHTML = '<p>No recommendations available.</p>';
            } else {
                data.recommended_artists.forEach(artist => {
                    const artistLink = document.createElement('a');
                    artistLink.href = `/artist_overview/${artist.id}/`;
                    artistLink.classList.add('recommended-artist-link');
                    artistLink.innerHTML = `
                        <div class="recommended-artist-item">
                            <img class="recommended-artist-image" src="${artist.image_url}" alt="${artist.name}">
                            <div id="recommended-artist-info">
                                <strong>${artist.name}</strong>
                            </div>
                        </div>
                    `;
                    artistRecommendationDiv.appendChild(artistLink);
                });
            }
        });
});
