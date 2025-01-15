function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    document.getElementById('current-time').textContent = timeString;
}

setInterval(updateTime, 1000); // Update time every second
updateTime(); // Initialize on page load

 // Initialize the tooltips
 $(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();  // Activate tooltips
});

document.addEventListener("DOMContentLoaded", function () {
    const hash = window.location.hash; // Get the fragment (e.g., #appointment)
    if (hash) {
        // Find the tab link corresponding to the fragment
        const targetTab = document.querySelector(`.nav-link[href="${hash}"]`);
        if (targetTab) {
            const tab = new bootstrap.Tab(targetTab); // Use Bootstrap's Tab API to activate the tab
            tab.show(); // Activate the tab programmatically
        }
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const uploadButton = document.querySelector('[data-bs-target="#uploadDocumentModal"]');
    uploadButton.addEventListener('click', () => console.log('Upload button clicked'));
});
