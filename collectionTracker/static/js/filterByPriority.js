document.addEventListener('DOMContentLoaded', function() {
    const priorityFilter = document.getElementById('priority-filter');
    const albumItems = document.querySelectorAll('.album-item');

    priorityFilter.addEventListener('change', function() {
        const selectedPriority = priorityFilter.value.toLowerCase();

        albumItems.forEach(function(item) {
            const priority = item.getAttribute('data-priority').toLowerCase();

            if (selectedPriority === '' || priority === selectedPriority) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });
});
