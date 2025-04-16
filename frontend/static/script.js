document.addEventListener("DOMContentLoaded", function () {
    // Navigation Buttons
    let btnLogin = document.getElementById("btn-login");
    let btnSignup = document.getElementById("btn-signup");
    let btnLogout = document.getElementById("btn-logout");
    let btnUpload = document.getElementById("btn-upload");  // Optional, if you have an upload nav button

    // Sections (make sure these IDs exist in your index.html)
    let loginSection = document.getElementById("login-section");
    let signupSection = document.getElementById("signup-section");
    let uploadSection = document.getElementById("upload-section");

    // Forms
    let loginForm = document.getElementById("login-form");
    let signupForm = document.getElementById("signup-form");
    let uploadForm = document.getElementById("upload-form");

    // File upload elements
    let fileInput = document.getElementById("imageUpload");
    let buttonPredict = document.getElementById("predict-button");
    let loadingIndicator = document.getElementById("loading");
    let predictionsContainer = document.getElementById("predictions-container");

    // Greeting element (user name display)
    let userGreeting = document.getElementById("user-greeting");

    // Validate that all DOM elements are present
    if (!btnLogin || !btnSignup || !btnLogout ||
        !loginSection || !signupSection || !uploadSection ||
        !loginForm || !signupForm || !uploadForm ||
        !fileInput || !buttonPredict || !loadingIndicator || !predictionsContainer || !userGreeting) {
        console.error("One or more required DOM elements are missing.");
        return;
    }

    // Helper: Show specific section and hide the others
    function showSection(section) {
        [loginSection, signupSection, uploadSection].forEach(sec => sec.classList.add("d-none"));
        section.classList.remove("d-none");
    }

    // Check user authentication
    function checkAuth() {
        const token = localStorage.getItem("token");
        const username = localStorage.getItem("username");

        if (token) {
            loginSection.classList.add("d-none");
            signupSection.classList.add("d-none");
            uploadSection.classList.remove("d-none");
            btnLogin.classList.add("d-none");
            btnSignup.classList.add("d-none");
            btnLogout.classList.remove("d-none");
            userGreeting.textContent = `Welcome, ${username || 'User'}!`;
        } else {
            uploadSection.classList.add("d-none");
            btnLogout.classList.add("d-none");
            btnLogin.classList.remove("d-none");
            btnSignup.classList.remove("d-none");
            userGreeting.textContent = '';
        }
    }

    checkAuth();

    // Navigation Button Listeners
    btnLogin.addEventListener("click", function () {
        showSection(loginSection);
    });

    btnSignup.addEventListener("click", function () {
        showSection(signupSection);
    });

    btnLogout.addEventListener("click", function () {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        checkAuth();
    });

    // Login Form Submission
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        let email = document.getElementById("loginEmail").value;
        let password = document.getElementById("loginPassword").value;

        try {
            let response = await fetch("http://127.0.0.1:5001/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            let data = await response.json();
            if (response.ok) {
                localStorage.setItem("token", data.token);
                localStorage.setItem("username", email.split('@')[0]);
                checkAuth();
            } else {
                alert(data.error || "Login failed");
            }
        } catch (error) {
            console.error("❌ Login Error:", error);
            alert("Login failed. See console for details.");
        }
    });

    // Signup Form Submission
    signupForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        let username = document.getElementById("signupUsername").value;
        let email = document.getElementById("signupEmail").value;
        let password = document.getElementById("signupPassword").value;

        try {
            let response = await fetch("http://127.0.0.1:5001/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, email, password })
            });

            let data = await response.json();
            if (response.ok) {
                alert("Signup successful! Please verify your email.");
                signupSection.classList.add("d-none");
                loginSection.classList.remove("d-none");
            } else {
                alert(data.error || "Signup failed");
            }
        } catch (error) {
            console.error("❌ Signup Error:", error);
            alert("Signup failed. See console for details.");
        }
    });

    // Function to get user location
    function getUserLocation(callback) {
        return new Promise((resolve, reject) => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        resolve({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        });
                    },
                    (error) => {
                        console.error("Error getting location:", error);
                        callback(null, null);
                    }
                );
            } else {
                console.error("Geolocation is not supported by this browser.");
                callback(null, null);
            }
        });
    }

    // Helper: Fetch treatment recommendations based on disease using treatments endpoint
    async function getTreatment(disease) {
        try {
            // Adjust the URL if needed; assuming the endpoint is defined as /treatments/<disease>
            console.log("🔥 Fetching treatment for disease:", disease);
            let response = await fetch(`http://127.0.0.1:5001/utils/treatments/${encodeURIComponent(disease)}`);
            if (!response.ok) {
                console.error(`❌ Failed to fetch treatment for ${disease}. Status: ${response.status}`);
                throw new Error("Failed to fetch treatment");
            }
            let data = await response.json();
            console.log("✅ Received treatment data:", data);
            return {
                treatment_text: data.treatment || "No treatment available",
                treatment_images: data.treatment_images || []
            };
        }   catch (error) {
            console.error("❌ Treatment fetch error:", error);
            return {
                treatment_text: "No treatment available",
                treatment_images: []
            };
        }
    }

    // Image Upload & Prediction Submission
    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        
        // Check if file input exists
        if (!fileInput) {
            alert("File input element is missing.");
            return;
        }

        let files = fileInput.files;
        if (files.length === 0) {
            alert("Please select at least one image.");
            return;
        }
        // Get user location
        let latitude = null;
        let longitude = null;
        try {
            // Wrap getUserLocation in a promise for async/await
            const position = await getUserLocation();
            latitude = position.latitude;
            longitude = position.longitude;
        } catch (error) {
            console.error("⚠️ Location fetch failed:", error);
            latitude = null;
            longitude = null;
        }

        //Create form data with files and location
        let formData = new FormData();
        for (let file of files) {
            formData.append("files", file);
        }
        formData.append("latitude", latitude);  // Add latitude
        formData.append("longitude", longitude); // Add longitude

        buttonPredict.innerText = "Working...";
        buttonPredict.disabled = true;
        loadingIndicator.style.display = "block";

        try {
            let token = localStorage.getItem("token");
            let response = await fetch("http://127.0.0.1:5001/upload", {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` },
                body: formData
            });

            let data = await response.json();
            console.log("🔥 Received Predictions:", data);
            displayPredictions(data.results, files);
        } catch (error) {
            console.error("❌ Upload Error:", error);
            alert("Image processing failed. See console for details.");
        } finally {
            buttonPredict.innerText = "Predict";
            buttonPredict.disabled = false;
            loadingIndicator.style.display = "none";
        }
    });

    // Display predictions with treatment recommendations
    async function displayPredictions(results, files) {
        predictionsContainer.innerHTML = "";

        // Create the table structure with an extra column for treatment.
        let table = document.createElement("table");
        table.className = "table table-striped table-bordered mt-3";
        table.innerHTML = `
        <thead class="table-dark">
            <tr>
              <th>Image</th>
              <th>Diagnostic</th>
              <th>Confidence Interval</th>
              <th>Treatment</th>
            </tr>
        </thead>
        <tbody></tbody>
    `   ;
        const tbody = table.querySelector("tbody");

        // Process each result asynchronously.
        let rowPromises = results.map(async (item, index) => {
            // Read the image file using FileReader.
            let imageData = await new Promise((resolve) => {
                let reader = new FileReader();
                reader.onload = function (e) {
                    resolve(e.target.result);
                };
                reader.readAsDataURL(files[index]);
            });

        // Format confidence and determine styling.
        let confidence = parseFloat(item.confidence);
        let confFormatted = confidence.toFixed(2);
        let color = confidence >= 80 ? "text-success" : confidence >= 60 ? "text-warning" : "text-danger";

        // Fetch treatment recommendation based on the predicted disease.
        let treatment = await getTreatment(item.disease);
        console.log("🔥 Treatment Data After getTreatment:", treatment);

        // Construct treatment HTML
        let treatmentHtml = `<p>${treatment.treatment_text}</p>`;
        if (treatment.treatment_images && treatment.treatment_images.length > 0) {
            treatmentHtml += '<div>';
            treatment.treatment_images.forEach(imgUrl => {
                treatmentHtml += `<img src="${imgUrl}" class="img-thumbnail" width="100">`;
            });
            treatmentHtml += '</div>';
        }
        
        console.log("🔥 Final Treatment HTML:", treatmentHtml);

        // Create HTML row for this result.
        let rowHtml = `
          <tr>
            <td><img src="${imageData}" class="img-thumbnail" width="100"></td>
            <td>${item.disease}</td>
            <td class="${color}"><strong>${confFormatted}%</strong></td>
            <td>${treatmentHtml}</td>
          </tr>
      `   ;
        tbody.insertAdjacentHTML('beforeend', rowHtml);
    });

    // Wait for all rows to be processed.
    await Promise.all(rowPromises);
    predictionsContainer.appendChild(table);
  }

  // Check for stored JWT token on load
  if (localStorage.getItem("token")) {
    btnLogout.classList.remove("d-none");
    showSection(uploadSection);
  }
});

    