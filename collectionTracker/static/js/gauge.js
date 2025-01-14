document.addEventListener('DOMContentLoaded', function() {
    var popularityValue = document.getElementById('gauge-fill').dataset.popularityValue;  // Dynamic value from Django context
    var maxValue = 100; // Maximum value for the hotness scale
    var percentage = (popularityValue / maxValue) * 100;

    // Update the gauge width based on the percentage
    var gaugeFill = document.getElementById('gauge-fill');
    var gaugeText = document.getElementById('gauge-text');
    
    gaugeFill.style.width = percentage + '%';
    gaugeText.textContent = 'Popularity: ' + popularityValue + '/' + maxValue;

    if (percentage < 50) {
        gaugeFill.classList.add('low');
    } else if (percentage < 80) {
        gaugeFill.classList.add('medium');
    } else {
        gaugeFill.classList.add('high');
    }
});
