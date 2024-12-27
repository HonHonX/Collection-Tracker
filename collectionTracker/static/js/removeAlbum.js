document.addEventListener('DOMContentLoaded', function () {
    // Select all "Remove" icons in the album grid
    document.querySelectorAll('.album-item .album-controls .icon').forEach(removeIcon => {
        removeIcon.addEventListener('click', function () {
            const albumItem = this.closest('.album-item'); // Get the parent album item
            const albumId = albumItem.dataset.albumId; // Get the album ID from data attribute
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // CSRF token

            // Confirm removal
            if (!confirm('Are you sure you want to remove this album from your collection?')) {
                return;
            }

            // Send a POST request to remove the album
            fetch('/collection/remove_album/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, // Include CSRF token in headers
                },
                body: JSON.stringify({ album_id: albumId }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message); // Show success message

                        // Remove the album item from the DOM
                        albumItem.remove();

                        // Optionally update the collection count
                        const collectionHeader = document.querySelector('.collection-header p');
                        const currentCount = parseInt(collectionHeader.textContent.match(/\d+/)[0], 10);
                        if (currentCount > 1) {
                            collectionHeader.textContent = `You have added ${currentCount - 1} album(s) to your collection.`;
                        } else {
                            collectionHeader.textContent = 'Your collection is empty.';
                        }
                    } else {
                        alert(data.error || data.message); // Show error message
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });
});
