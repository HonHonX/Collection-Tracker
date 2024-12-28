document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.album-item .album-controls .icon').forEach(removeIcon => {
        removeIcon.addEventListener('click', function () {
            const albumItem = this.closest('.album-item');
            const albumId = albumItem.dataset.albumId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            if (!albumId) {
                console.error('No album ID found for the selected item.');
                alert('Could not identify the album. Please try again.');
                return;
            }

            if (!confirm('Are you sure you want to remove this album from your collection?')) {
                return;
            }

            fetch('/collection/remove_album/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ album_id: albumId }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        albumItem.remove();
                        const collectionHeader = document.querySelector('.collection-header p');
                        const currentCount = parseInt(collectionHeader.textContent.match(/\d+/)[0], 10);
                        if (currentCount > 1) {
                            collectionHeader.textContent = `You have added ${currentCount - 1} album(s) to your collection.`;
                        } else {
                            collectionHeader.textContent = 'Your collection is empty.';
                        }
                    } else {
                        console.error('Backend error:', data);
                        alert(data.error || data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });
});
