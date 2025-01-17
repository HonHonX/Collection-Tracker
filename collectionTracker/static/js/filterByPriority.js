document.addEventListener('DOMContentLoaded', function() {
    const priorityFilter = document.getElementById('priority-filter');
    const albumItems = document.querySelectorAll('.album-item');

    priorityFilter.addEventListener('change', function() {
        const selectedPriority = priorityFilter.value.toLowerCase();
        console.log('Selected Priority:', selectedPriority); // Debugging line

        albumItems.forEach(function(item) {
            const priority = item.getAttribute('data-priority').toLowerCase();
            console.log('Album Priority:', priority); // Debugging line

            if (selectedPriority === '' || priority === selectedPriority) {
                console.log(`Showing item with priority: ${priority}`); // Debugging line
                item.style.display = 'block';
            } else {
                console.log(`Hiding item with priority: ${priority}`); // Debugging line
                item.style.display = 'none';
            }
        });
    });
});
