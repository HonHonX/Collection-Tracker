function togglePopup(popupId) {
    const popup = document.getElementById(popupId);
    if (popup) {
        popup.classList.toggle('visible'); // Assuming you use a 'visible' class to show/hide the popup
    } else {
        console.error(`Popup with ID '${popupId}' not found.`);
    }
}