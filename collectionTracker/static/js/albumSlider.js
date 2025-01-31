// Implement slider scroll behavior with mouse interaction
document.querySelectorAll('.album-slider, #events-slider').forEach(slider => {
    slider.addEventListener('wheel', (event) => {
        event.preventDefault(); // Prevent vertical scrolling
        slider.scrollBy({
            left: event.deltaY, // Use vertical scroll input for horizontal scrolling
            behavior: 'smooth'
        });
    });
});