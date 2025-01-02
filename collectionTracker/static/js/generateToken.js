document.getElementById('generate-token-button').addEventListener('click', function() {
    fetch("/friends/generate_token/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('token-display').textContent = data.token;
        document.getElementById('wishlist-share-link').href = "/friends/share/" + data.token + "/wishlist/";
        document.getElementById('collection-share-link').href = "/friends/share/" + data.token + "/collection/";
    });
});
