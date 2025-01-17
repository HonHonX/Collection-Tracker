let currentIndex = 0; // Start with the first slide
let autoSlideInterval;

// Function to initialize the carousel
function initializeCarousel() {
    const carousel = document.querySelector('.carousel');
    const slides = document.querySelectorAll('.carousel-item');

    // Adjust the transform to show the actual first slide
    const slideWidth = slides[0].offsetWidth + 20; // Including margin
    const offset = slideWidth * currentIndex;
    carousel.style.transform = `translateX(-${offset}px)`;
}

// Function to update the album details
function updateAlbumDetails() {
    const activeSlide = document.querySelector('.carousel-item.active');
    const albumTitle = activeSlide.dataset.title;
    const albumArtist = activeSlide.dataset.artist;

    // Update the album details in the DOM
    document.getElementById('album-title').textContent = albumTitle;
    document.getElementById('album-artist').textContent = `By ${albumArtist}`;
}

// Function to update the carousel and indicators
function updateActiveSlide(skipTransition = false) {
    const slides = document.querySelectorAll('.carousel-item');
    const indicators = document.querySelectorAll('.indicator');

    // Reset all slides and indicators
    slides.forEach((slide, index) => {
        slide.classList.remove('active');
        if (index === currentIndex) {
            slide.classList.add('active');
        }
    });

    indicators.forEach((indicator, index) => {
        indicator.classList.remove('active');
        if (index === currentIndex) {
            indicator.classList.add('active');
        }
    });

    // Adjust the carousel's transform
    const carousel = document.querySelector('.carousel');
    const slideWidth = slides[0].offsetWidth + 20; // Including margin
    carousel.style.transition = skipTransition ? 'none' : 'transform 0.8s ease';
    carousel.style.transform = `translateX(-${currentIndex * slideWidth}px)`;

    // Update the album details
    updateAlbumDetails();
}

// Function to move to the next or previous slide
function moveSlide(direction) {
    const slides = document.querySelectorAll('.carousel-item');

    // Move to the next or previous slide
    currentIndex = (currentIndex + direction + slides.length) % slides.length;
    updateActiveSlide();
    resetAutoSlide();
}

// Function to start the auto-slide
function startAutoSlide() {
    autoSlideInterval = setInterval(() => {
        moveSlide(1);
    }, 3000); // Change slide every 3 seconds
}

// Function to reset auto-slide when manually navigating
function resetAutoSlide() {
    clearInterval(autoSlideInterval);
    startAutoSlide();
}

// Function to remove an album from the carousel
function removeAlbumFromCarousel(albumId) {
    const carousel = document.querySelector('.carousel');
    const slides = document.querySelectorAll('.carousel-item');

    slides.forEach((slide, index) => {
        if (slide.dataset.albumId === albumId) {
            carousel.removeChild(slide);
            if (index === currentIndex) {
                currentIndex = (currentIndex - 1 + slides.length) % slides.length;
            }
        }
    });

    // Update the carousel immediately
    updateActiveSlide(true);
}

// Event listeners for mouse interaction
document.addEventListener('DOMContentLoaded', () => {
    initializeCarousel(); // Set initial position
    updateActiveSlide(true); // Highlight the first image without animation
    startAutoSlide(); // Start auto-slide

    // Pause auto-slide on hover
    const carouselContainer = document.querySelector('.carousel-container');
    carouselContainer.addEventListener('mouseenter', () => clearInterval(autoSlideInterval));
    carouselContainer.addEventListener('mouseleave', startAutoSlide);
});
