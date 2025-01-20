document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('price-chart');
    if (!canvas) {
        return;
    }
    const albumId = canvas.dataset.albumId;
    const url = canvas.dataset.url;
    const url_predict = canvas.dataset.urlpred;

    const colorPrices = getComputedStyle(document.documentElement).getPropertyValue('--accent100').trim();
    const colorPricesPredict = getComputedStyle(document.documentElement).getPropertyValue('--accentVariantB100').trim();

    Promise.all([ 
        fetch(url).then(response => response.json()), 
        fetch(url_predict).then(response => response.json()) 
    ])
    .then(([data, predictData]) => {

        const labels = data.map(entry => entry.date);
        const prices = data.map(entry => parseFloat(entry.price).toFixed(2));
        const predictLabels = predictData.map(entry => entry.ds);
        const predictPrices = predictData.map(entry => parseFloat(entry.yhat).toFixed(2));

        const today = new Date();
        const futureDates = [];
 
        for (let i = 0; i < 8; i++) {  // Include one more day (8 days total)
            let futureDate = new Date(today);
            futureDate.setDate(today.getDate() + i); // Generate future dates (next 8 days)
            futureDates.push(futureDate.toISOString().split('T')[0]); 
        }

        const combinedLabels = [...labels, ...futureDates];
        const combinedPrices = [...prices, ...predictPrices]; 

        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: combinedLabels,
                datasets: [
                    {
                        label: 'Price (in €)',
                        data: combinedPrices.slice(0, labels.length), 
                        borderColor: colorPrices,
                        borderWidth: 1,
                        fill: false,
                        pointRadius: 4,
                        hitRadius: 10
                    },
                    {
                        label: 'Predicted Price (in €)',
                        data: combinedPrices.slice(labels.length), 
                        borderColor: colorPricesPredict,
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
                        },
                        ticks: {
                            color: 'white',
                            font: {
                                family: 'Montserrat',
                            }
                        }
                    },
                    y: {
                        beginAtZero: false,
                        ticks: {
                            color: 'white',
                            font: {
                                family: 'Montserrat', 
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'white',
                            font: {
                                family: 'Montserrat',
                            }
                        }
                    }
                }
            }
        });
    })
    .catch(error => console.error('Error fetching data:', error)); // Debug: Log fetch errors
});
