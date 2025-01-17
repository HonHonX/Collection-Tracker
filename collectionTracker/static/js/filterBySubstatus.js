document.addEventListener('DOMContentLoaded', function() {
    const substatusFilter = document.getElementById('substatus-filter');
    const albumItems = document.querySelectorAll('.album-item');

    substatusFilter.addEventListener('change', function() {
        const selectedSubstatus = substatusFilter.value.toLowerCase();
        console.log('Selected Substatus:', selectedSubstatus); // Debugging line

        albumItems.forEach(function(item) {
            const substatus = item.getAttribute('data-substatus').toLowerCase();
            console.log('Album Substatus:', substatus); // Debugging line

            if (selectedSubstatus === '' || substatus === selectedSubstatus) {
                console.log(`Showing item with substatus: ${substatus}`); // Debugging line
                item.style.display = 'block';
            } else {
                console.log(`Hiding item with substatus: ${substatus}`); // Debugging line
                item.style.display = 'none';
            }
        });
    });
});
