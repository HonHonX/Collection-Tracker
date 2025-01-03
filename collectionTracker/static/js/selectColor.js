document.addEventListener('DOMContentLoaded', function() {
    const selectedOption = document.getElementById('selected-option');
    const optionsContainer = document.querySelector('.options-container');
    const optionsList = document.querySelectorAll('.option');

    selectedOption.addEventListener('click', () => {
        optionsContainer.classList.toggle('active');
    });

    optionsList.forEach(option => {
        option.addEventListener('click', () => {
            selectedOption.innerHTML = option.innerHTML;
            document.getElementById('color_scheme').value = option.getAttribute('data-value');
            optionsContainer.classList.remove('active');
        });
    });
});