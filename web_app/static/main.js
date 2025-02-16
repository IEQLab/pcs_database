document.addEventListener("DOMContentLoaded", function () {
    console.log("Main.js loaded!");

    // Global Page Navigation Handler
    function showSection(sectionId) {
        document.querySelectorAll(".content-section").forEach(section => section.classList.remove("active-section"));
        document.getElementById(sectionId).classList.add("active-section");

        // Ensure graph updates when switching to Graph section
        if (sectionId === "graph-section") {
            updateChart();
        }
    }

    // Make showSection available globally
    window.showSection = showSection;

    // Automatically show overview section on load
    showSection("overview-section");
});
