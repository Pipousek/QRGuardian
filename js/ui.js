// UI enhancement functionality
const UI = {
    // Initialize UI enhancements
    initialize: function() {
        // Apply touch-specific styling if on a touch device
        if ('ontouchstart' in window) {
            document.querySelectorAll('.btn').forEach(btn => {
                btn.classList.add('py-2');
            });
        }

        // Initialize Bootstrap tooltips if Bootstrap is loaded
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }
};