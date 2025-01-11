document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('price-chart');
    const albumId = canvas.dataset.albumId;
    const url = canvas.dataset.url;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('Fetched data:', data); // Debug: Log fetched data

            // Ensure data is correctly formatted
            const labels = data.map(entry => entry.date);
            const prices = data.map(entry => entry.price);

            console.log('Labels:', labels); // Debug: Log labels
            console.log('Prices:', prices); // Debug: Log prices

            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Price',
                        data: prices,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        fill: false,
                        pointRadius: 3, // Ensure points are visible
                        hitRadius: 10 // Increase hit radius for better interaction
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day'
                            }
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            console.log('Chart rendered'); // Debug: Log chart rendering
        })
        .catch(error => console.error('Error fetching data:', error)); // Debug: Log fetch errors
});
