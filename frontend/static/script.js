document.getElementById("file-input").addEventListener("change", function (event) {
    let files = event.target.files;
    let previewContainer = document.getElementById("image-preview");
    previewContainer.innerHTML = "";  // Clear previous previews

    if (files.length > 0) {
        for (let file of files) {
            let reader = new FileReader();
            reader.onload = function (e) {
                let imgElement = document.createElement("img");
                imgElement.src = e.target.result;
                imgElement.classList.add("preview-image");
                previewContainer.appendChild(imgElement);
            };
            reader.readAsDataURL(file);
        }
    }
});

document.getElementById("upload-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    let fileInput = document.getElementById("file-input");
    if (fileInput.files.length === 0) {
        alert("Please select image files.");
        return;
    }

    let formData = new FormData();
    for (let file of fileInput.files) {
        formData.append("files", file); // Append multiple files
    }

    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("result").innerHTML = "";

    try {
        let response = await fetch("http://127.0.0.1:5000/upload", {
            method: "POST",
            body: formData,
            headers: {
                "Accept": "application/json"
            }
        });

        let data = await response.json();
        document.getElementById("loading").classList.add("hidden");

        if (response.ok) {
            let resultContainer = document.getElementById("result");
            resultContainer.innerHTML = "";

            data.results.forEach((res, index) => {
                let resultDiv = document.createElement("div");
                resultDiv.classList.add("result-item");
                resultDiv.innerHTML = `
                    <strong>File:</strong> ${res.filename} <br>
                    <strong>Prediction:</strong> ${res.prediction} <br>
                    <strong>Confidence:</strong> ${(res.confidence * 100).toFixed(2)}% <br><br>
                `;
                resultContainer.appendChild(resultDiv);
            });
        } else {
            document.getElementById("result").innerHTML = `Error: ${data.error}`;
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("result").innerHTML = `Network error. Please try again.`;
    }
});