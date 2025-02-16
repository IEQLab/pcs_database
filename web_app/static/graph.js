document.addEventListener("DOMContentLoaded", function () {
    console.log("Graph.js loaded successfully!");

    let ctx = document.getElementById("mainChart").getContext("2d");
    let mainChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: [],
            datasets: [{
                label: "Delta_P_All",
                data: [],
                backgroundColor: "rgba(54, 162, 235, 0.5)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1
            }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });

    async function updateChart() {
        try {
            console.log("Fetching chart data...");
            const response = await fetch(`/chart_data`);
            const chartData = await response.json();

            console.log("Chart Data:", chartData);

            if (chartData.labels.length === 0) {
                console.warn("No data received for chart.");
                return;
            }

            mainChart.data.labels = chartData.labels;
            mainChart.data.datasets[0].data = chartData.data;
            mainChart.update();
        } catch (error) {
            console.error("Error fetching chart data:", error);
        }
    }

    // Load chart when Graph tab is selected
    document.querySelector('[onclick="showSection(\'graph-section\')"]').addEventListener("click", updateChart);

    // Load chart on page load
    window.onload = updateChart;
});
