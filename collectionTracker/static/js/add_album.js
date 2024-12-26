document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.album-controls .icon').forEach(addIcon => {
        addIcon.addEventListener('click', function () {
            console.log('Add button clicked');  // Log when the button is clicked

            const albumItem = this.closest('.album-item');
            const albumId = albumItem.dataset.albumId;
            const albumName = albumItem.dataset.albumName;
            const albumType = albumItem.dataset.albumType;
            const releaseDate = albumItem.dataset.releaseDate;
            const imageUrl = albumItem.dataset.imageUrl;

            // Check if data attributes are correct
            console.log('Album Data:', albumId, albumName, albumType, releaseDate, imageUrl);

            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            console.log('CSRF Token:', csrfToken);

            // Send the POST request to add the album to the user's collection
            fetch('/add_album/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,  // Pass the CSRF token in the header
                },
                body: JSON.stringify({
                    album_id: albumId,
                    album_name: albumName,
                    album_type: albumType,
                    release_date: releaseDate,
                    image_url: imageUrl,
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);  // Success message
                } else {
                    alert(data.error || data.message);  // Error message
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

