// Main application initialization
document.addEventListener("DOMContentLoaded", function() {
    // Clear all file inputs on page load
    FileUpload.clearAll();

    // Initialize file drop functionality
    FileUpload.initialize();

    // Update download links
    Downloads.updateLinks();

    // Handle download for generated QR code
    Downloads.downloadGeneratedQR();

    // Initialize navigation
    Navigation.initialize();
    
    // Initialize UI enhancements
    UI.initialize();
});