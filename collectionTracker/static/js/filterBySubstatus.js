document.addEventListener('DOMContentLoaded', function() {
    const substatusFilter = document.getElementById('substatus-filter');
    const albumItems = document.querySelectorAll('.album-item');

    substatusFilter.addEventListener('change', function() {
        const selectedSubstatus = substatusFilter.value.toLowerCase();

        albumItems.forEach(function(item) {
            const substatus = item.getAttribute('data-substatus').toLowerCase();

            if (selectedSubstatus === '' || substatus === selectedSubstatus) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });
});
