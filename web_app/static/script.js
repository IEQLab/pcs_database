document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript loaded successfully!");

    // Initialize the empty chart
    let ctx = document.getElementById("myChart").getContext("2d");
    let myChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: [],  // Empty labels initially
            datasets: [{
                label: "Delta_P_All",
                data: [],  // Empty data initially
                backgroundColor: "rgba(54, 162, 235, 0.5)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Function to fetch and update the table & chart
    async function handleFilterUpdate() {
        let formData = new FormData(document.getElementById("filter-form"));

        try {
            // Fetch table data
            const tableResponse = await fetch("/filter", {
                method: "POST",
                body: formData
            });
            const tableData = await tableResponse.text();

            // Update the table body dynamically
            document.getElementById("table-body").innerHTML = new DOMParser()
                .parseFromString(tableData, "text/html")
                .querySelector("#table-body").innerHTML;

            // Enable CSV download button after filtering
            document.getElementById("download-btn").disabled = false;

            // Update hidden fields for CSV export
            document.getElementById("csv_pcsid").value = document.getElementById("pcsid").value;
            document.getElementById("csv_pcsname").value = document.getElementById("pcsname").value;

            // Update the chart
            await updateChart();
        } catch (error) {
            console.error("Error updating table and chart:", error);
        }
    }

    // Function to update Chart.js dynamically **without destroying it**
    async function updateChart() {
        const pcsid = document.getElementById("pcsid").value;
        const pcsname = document.getElementById("pcsname").value;

        try {
            // Fetch filtered chart data from Flask API
            const response = await fetch(`/chart_data?pcsid=${pcsid}&pcsname=${pcsname}`);
            const chartData = await response.json();

            // Update chart data directly without recreating the chart
            myChart.data.labels = chartData.labels;  // X-axis: PCS_Name
            myChart.data.datasets[0].data = chartData.data;  // Y-axis: Delta_P_All
            myChart.update();  // Refresh the chart with new data
        } catch (error) {
            console.error("Error fetching chart data:", error);
        }
    }

    // Debounce to prevent multiple requests
    let debounceTimer;
    function debounceUpdate() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(handleFilterUpdate, 300);
    }

    // Event listeners for filter changes
    document.getElementById("pcsid").addEventListener("change", debounceUpdate);
    document.getElementById("pcsname").addEventListener("input", debounceUpdate);

    // Load initial chart frame on page load
    updateChart();
});
