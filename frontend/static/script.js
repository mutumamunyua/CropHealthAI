document.addEventListener("DOMContentLoaded", function () {
    console.log("🚀 Script loaded successfully!");

    document.body.innerHTML = document.body.innerHTML.replace(/\b\d+\b/g, '');
    
    let form = document.getElementById("upload-form");
    let fileInput = document.getElementById("imageUpload");
    let button = document.getElementById("predict-button");
    let loadingIndicator = document.getElementById("loading");
    let predictionsContainer = document.getElementById("predictions-container");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        let files = fileInput.files;
        if (files.length === 0) {
            alert("Please select at least one image.");
            return;
        }

        let formData = new FormData();
        for (let file of files) {
            formData.append("files", file);
        }

        // Disable button and show loading
        button.innerText = "Working...";
        button.disabled = true;
        loadingIndicator.style.display = "block";

        try {
            let response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            let data = await response.json();
            console.log("🔥 Received Predictions:", data);

            showPredictions(data.results, files);
        } catch (error) {
            console.error("❌ Error:", error);
            alert("Error processing the images. Check console for details.");
        } finally {
            // Reset button text
            button.innerText = "Predict";
            button.disabled = false;
            loadingIndicator.style.display = "none";
        }
    });

    function showPredictions(results, files) {
        predictionsContainer.innerHTML = ""; // Clear previous results
    
        if (!results || results.length === 0) {
            predictionsContainer.innerHTML = "<p class='text-danger'>No predictions available.</p>";
            return;
        }
    
        let table = document.createElement("table");
        table.className = "table table-striped table-bordered mt-3";
    
        let thead = document.createElement("thead");
        thead.className = "table-dark";
        thead.innerHTML = `
            <tr>
                <th>Image</th>
                <th>Diagnostic</th>
                <th>Confidence Interval</th>
            </tr>
        `;
    
        let tbody = document.createElement("tbody");
    
        results.forEach((item, index) => {
            let confidence = parseFloat(item.confidence);
            let confidenceColor = confidence >= 80 ? "text-success" :
                                  confidence >= 60 ? "text-warning" : "text-danger";
    
            let reader = new FileReader();
            reader.onload = function (e) {
                let row = document.createElement("tr");
    
                let imgCell = document.createElement("td");
                let img = document.createElement("img");
                img.src = e.target.result;
                img.className = "img-thumbnail";
                img.width = 100;
                imgCell.appendChild(img);
    
                let diseaseCell = document.createElement("td");
                diseaseCell.textContent = item.disease;
    
                let confidenceCell = document.createElement("td");
                confidenceCell.className = confidenceColor;
                confidenceCell.innerHTML = `<strong>${confidence}%</strong>`;
    
                row.appendChild(imgCell);
                row.appendChild(diseaseCell);
                row.appendChild(confidenceCell);
    
                tbody.appendChild(row);
            };
            reader.readAsDataURL(files[index]);
        });
    
        table.appendChild(thead);
        table.appendChild(tbody);
        predictionsContainer.appendChild(table);
    }
});
