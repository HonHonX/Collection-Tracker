function toggleStatus(albumId) {
    const url = `/update_album_status/${albumId}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({
            album_id: albumId
        })
    })
    .then(response => response.json())
    .then(data => {
        const albumTile = document.querySelector(`.album-tile[data-id="${albumId}"] .heart-icon`);
        if (data.new_status) {
            albumTile.classList.add('active');
        } else {
            albumTile.classList.remove('active');
        }
    })
    .catch(error => console.error('Error:', error));
}
