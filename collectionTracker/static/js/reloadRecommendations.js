document.getElementById('reload-recommendations-icon').addEventListener('click', function() {

    var imageUrl = this.getAttribute('data-image-url');
    // Show SweetAlert2 notification
    Swal.fire({
        title: 'Refreshing Recommendations',
        text: 'Stay tuned! Bopsy is sorting through beats and bops to find the perfect artists for you.',
        imageUrl: imageUrl,
        imageWidth: 100,
        imageHeight: 100, 
        imageAlt: 'Bopsy Logo',
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        willOpen: () => {
            Swal.showLoading();
        }
    });

    fetch("/reload-recommendations/")
        .then(response => response.json())
        .then(data => {
            // Close the SweetAlert2 notification
            Swal.close();

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
        })
        .catch(error => {
            Swal.close();
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: 'Something went wrong! Please try again later.'
            });
        });
});
