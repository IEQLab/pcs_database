document.addEventListener("DOMContentLoaded", function () {
    console.log("Overview.js loaded!");

    let overviewData = [
        { title: "Koala", description: "Koalas like to sleep." },
        { title: "Lego", description: "Koalas like Lego." },
        { title: "McDonald", description: "Koalas like McDonald." },
        { title: "Sushi", description: "Koalas like sushi." },
        { title: "Lion", description: "Koalas do not like lions." },
    ];

    function loadOverview() {
        let container = document.getElementById("overview-container");
        container.innerHTML = "";

        overviewData.forEach((item, index) => {
            let card = document.createElement("div");
            card.classList.add("col-md-4", "mb-4");

            // Use placeholder image
            let imagePath = `/image/koala.jpg`;

            card.innerHTML = `
                <div class="card shadow-sm">
                    <img src="${imagePath}" class="card-img-top" alt="${item.title}">
                    <div class="card-body">
                        <h5 class="card-title">${item.title}</h5>
                        <p class="card-text">${item.description}</p>
                    </div>
                </div>
            `;

            container.appendChild(card);
        });
    }

    // Load overview data when the Overview tab is clicked
    document.querySelector('[onclick="showSection(\'overview-section\')"]').addEventListener("click", loadOverview);

    // Load overview on page load if it's the default section
    window.onload = loadOverview;
});
