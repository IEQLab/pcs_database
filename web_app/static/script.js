document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript loaded successfully!");

    document.getElementById("filter-form").addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page reload

        let formData = new FormData(this);

        fetch("/filter", {
            method: "POST",
            body: formData
        })
        .then(response => response.text()) // Expect HTML response
        .then(data => {
            document.getElementById("table-body").innerHTML = new DOMParser()
                .parseFromString(data, "text/html")
                .querySelector("#table-body").innerHTML;

            // Enable the CSV download button
            document.getElementById("download-btn").disabled = false;

            // Update hidden fields for CSV export
            document.getElementById("csv_pcsid").value = document.getElementById("pcsid").value;
            document.getElementById("csv_pcsname").value = document.getElementById("pcsname").value;
        })
        .catch(error => console.error("Error:", error));
    });
});

//document.addEventListener("DOMContentLoaded", function () {
//    console.log("JavaScript loaded successfully!");
//
//    document.getElementById("filter-form").addEventListener("submit", function (event) {
//        event.preventDefault(); // ページリロードを防ぐ
//
//        let formData = {
//            pcid: document.getElementById("pcsid").value,
//            pcsname: document.getElementById("pcsname").value
//        };
//
//        fetch("/filter", {
//            method: "POST",
//            headers: {
//                "Content-Type": "application/json"
//            },
//            body: JSON.stringify(formData)
//        })
//        .then(response => response.json())
//        .then(data => {
//            updateTable(data);
//        })
//        .catch(error => console.error("Error:", error));
//    });
//
//    function updateTable(data) {
//        let tableBody = document.getElementById("table-body");
//        tableBody.innerHTML = "";
//
//        if (data.length === 0) {
//            tableBody.innerHTML = "<tr><td colspan='100%'>No matching data found</td></tr>";
//            return;
//        }
//
//        data.forEach(row => {
//            let tr = document.createElement("tr");
//            Object.values(row).forEach(value => {
//                let td = document.createElement("td");
//                td.textContent = value;
//                tr.appendChild(td);
//            });
//            tableBody.appendChild(tr);
//        });
//    }
//});
