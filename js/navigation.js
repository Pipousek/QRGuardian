// Navigation functionality
const Navigation = {
    // Show a specific page
    showPage: function(pageId) {
        document.querySelectorAll(".page").forEach(page => {
            page.classList.remove("active");
        });

        const selectedPage = document.getElementById(pageId);
        if (selectedPage) {
            selectedPage.classList.add("active");
        }

        document.querySelectorAll("nav a").forEach(link => {
            if (link.getAttribute("href") === `#${pageId}`) {
                link.classList.add("active");
            } else {
                link.classList.remove("active");
            }
        });
    },
    
    // Initialize navigation
    initialize: function() {
        // Handle QR mode changes
        document.querySelector("#qr_mode")?.addEventListener("change", function() {
            document.querySelectorAll(".input-section").forEach(section => {
                section.classList.remove("active");
            });

            const sectionId = this.value + "-section";
            const section = document.getElementById(sectionId);
            if (section) {
                section.classList.add("active");
            }
        });

        // Set initial page from hash or default to 'create'
        const initialPage = window.location.hash.substring(1) || "create";
        this.showPage(initialPage);

        // Listen for hash changes
        window.addEventListener("hashchange", () => {
            const pageId = window.location.hash.substring(1);
            this.showPage(pageId);
        });
    }
};