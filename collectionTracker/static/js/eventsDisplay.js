document.addEventListener('DOMContentLoaded', function () {
    const eventsBlock = document.getElementById('artist-events-block');
    const artistName = eventsBlock.dataset.artistName;
    const eventsList = document.getElementById('events-slider');

    if (artistName) {
        fetch(`/fetch-artist-events/${encodeURIComponent(artistName)}/`)
            .then(response => response.json())
            .then(data => {
                eventsList.innerHTML = '';  // Clear the "Loading..." message

                if (data.events.length > 0) {
                    data.events.forEach(event => {
                        const div = document.createElement('div');
                        div.className = 'slider-item';
                        div.innerHTML = `
                            ${event.image ? `<img src="${event.image}" class="event-image" alt="Event Image"><br>` : ''}
                            <strong>${event.name}</strong><br>
                            Date: ${event.start_date} ${event.start_time ? 'at ' + event.start_time.slice(0, 5) : ''}<br>
                            Venue: ${event._embedded.venues[0].name}<br>
                            Address: ${event.address}, ${event.city}${event.state ? ', ' + event.state : ''}, ${event.country}<br>
                            <a href="${event.url}" target="_blank">More Info</a>
                        `;
                        eventsList.appendChild(div);
                    });
                } else {
                    eventsList.innerHTML = '<div class="slider-item">No events found.</div>';
                }
            })
            .catch(err => {
                eventsList.innerHTML = '<div class="slider-item">Error fetching events.</div>';
                console.error(err);
            });
    }
});
