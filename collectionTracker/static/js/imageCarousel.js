let currentIndex = 1; // Start with the middle slide
let autoSlideInterval;

// Function to initialize the carousel with clones
function initializeCarousel() {
    const carousel = document.querySelector('.carousel');
    const slides = document.querySelectorAll('.carousel-item');

    // Clone the first and last slides
    const firstSlide = slides[0].cloneNode(true);
    const lastSlide = slides[slides.length - 1].cloneNode(true);

    // Append and prepend the cloned slides
    carousel.appendChild(firstSlide);
    carousel.insertBefore(lastSlide, slides[0]);

    // Adjust the transform to show the actual first slide
    const slideWidth = slides[0].offsetWidth + 20; // Including margin
    const offset = slideWidth * currentIndex;
    carousel.style.transform = `translateX(-${offset}px)`;

    // Add the event listener for transitionend to handle seamless looping
    carousel.addEventListener('transitionend', handleSeamlessLoop);
}

// Function to handle seamless looping after the transition
function handleSeamlessLoop() {
    const carousel = document.querySelector('.carousel');
    const slides = document.querySelectorAll('.carousel-item');

    // Check if we've transitioned to a cloned slide
    if (currentIndex === 0) {
        // Jump to the last real slide without animation
        const slideWidth = slides[0].offsetWidth + 20;
        currentIndex = slides.length - 3; // Last real slide index
        carousel.style.transition = 'none';
        carousel.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
    } else if (currentIndex === slides.length - 1) {
        // Jump to the first real slide without animation
        const slideWidth = slides[0].offsetWidth + 20;
        currentIndex = 1; // First real slide index
        carousel.style.transition = 'none';
        carousel.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
    }
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
        if (index === currentIndex - 1) {
            // Adjust index for real slides
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

// Event listeners for mouse interaction
document.addEventListener('DOMContentLoaded', () => {
    initializeCarousel(); // Clone slides and set initial position
    updateActiveSlide(true); // Highlight the middle image without animation
    startAutoSlide(); // Start auto-slide

    // Pause auto-slide on hover
    const carouselContainer = document.querySelector('.carousel-container');
    carouselContainer.addEventListener('mouseenter', () => clearInterval(autoSlideInterval));
    carouselContainer.addEventListener('mouseleave', startAutoSlide);
});
