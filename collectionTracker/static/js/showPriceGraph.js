document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('price-chart');
    const albumId = canvas.dataset.albumId;
    const url = canvas.dataset.url;
    const url_predict = canvas.dataset.urlpred;

    Promise.all([ 
        fetch(url).then(response => response.json()), 
        fetch(url_predict).then(response => response.json()) 
    ])
    .then(([data, predictData]) => {
        console.log('Fetched original data:', data); // Debug: Log original data
        console.log('Fetched predicted data:', predictData); // Debug: Log predicted data

        const labels = data.map(entry => entry.date);
        const prices = data.map(entry => entry.price);
        const predictLabels = predictData.map(entry => entry.ds);
        const predictPrices = predictData.map(entry => entry.yhat);

        const today = new Date();
        const upcomingDays = [];
        const futureDates = [];

        for (let i = 1; i <= 7; i++) {
            let futureDate = new Date(today);
            futureDate.setDate(today.getDate() + i); // Generate future dates (next 7 days)
            futureDates.push(futureDate.toISOString().split('T')[0]); 
            upcomingDays.push({ date: futureDates[i - 1], price: null });
        }

        const combinedLabels = [...labels, ...futureDates];
        const combinedPrices = [...prices, ...predictPrices]; 

        console.log('Labels (combined):', combinedLabels); 
        console.log('Prices (combined):', combinedPrices);

        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: combinedLabels,
                datasets: [
                    {
                        label: 'Price',
                        data: prices, 
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        fill: false,
                        pointRadius: 4,
                        hitRadius: 10
                    },
                    {
                        label: 'Predicted Price',
                        data: predictPrices, 
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        borderDash: [5, 5], 
                        fill: false,
                        pointRadius: 4,
                        hitRadius: 10
                    }
                ]
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
                        beginAtZero: false
                    }
                }
            }
        });

        console.log('Chart rendered with predicted data and upcoming days'); // Debug: Log chart rendering
    })
    .catch(error => console.error('Error fetching data:', error)); // Debug: Log fetch errors
});
