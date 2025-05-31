document.addEventListener("DOMContentLoaded", function () {
    // 🌐 Step 1: Define dynamic backend base URL
    const backendBaseURL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:5001"
        : "https://crop-health-ai.onrender.com";

    // Navigation Buttons
    let btnLogin = document.getElementById("btn-login");
    let btnSignup = document.getElementById("btn-signup");
    let btnLogout = document.getElementById("btn-logout");
    let btnUpload = document.getElementById("btn-upload");  // Optional, if you have an upload nav button
    let btnRegisterAgrovet = document.getElementById("btn-register-agrovet");
    let btnRegisterExtensionWorker = document.getElementById("btn-register-extension-worker");

    // Sections (make sure these IDs exist in your index.html)
    let loginSection = document.getElementById("login-section");
    let signupSection = document.getElementById("signup-section");
    let uploadSection = document.getElementById("upload-section");
    let registerAgrovetSection = document.getElementById("register-agrovet-section");
    let registerExtensionWorkerSection = document.getElementById("register-extension-worker-section");

    // Forms
    let loginForm = document.getElementById("login-form");
    let signupForm = document.getElementById("signup-form");
    let uploadForm = document.getElementById("upload-form");
    let registerAgrovetForm = document.getElementById("register-agrovet-form");
    let registerExtensionWorkerForm = document.getElementById("register-extension-worker-form");

    // File upload elements
    let fileInput = document.getElementById("imageUpload");
    let buttonPredict = document.getElementById("predict-button");
    let loadingIndicator = document.getElementById("loading");
    let predictionsContainer = document.getElementById("predictions-container");

    // Greeting element (user name display)
    let userGreeting = document.getElementById("user-greeting");

    // Response elements for registration
    let agrovetResponse = document.getElementById("agrovet-response");
    let extensionWorkerResponse = document.getElementById("extension-worker-response");

     // Validate that all DOM elements are present
     if (!btnLogin || !btnSignup || !btnLogout ||
        !btnRegisterAgrovet || !btnRegisterExtensionWorker ||
        !loginSection || !signupSection || !uploadSection ||
        !registerAgrovetSection || !registerExtensionWorkerSection ||
        !loginForm || !signupForm || !uploadForm ||
        !registerAgrovetForm || !registerExtensionWorkerForm ||
        !fileInput || !buttonPredict || !loadingIndicator || !predictionsContainer || !userGreeting ||
        !agrovetResponse || !extensionWorkerResponse) {
        console.error("One or more required DOM elements are missing.");
        return;
    }

    // Helper: Show specific section and hide the others
    function showSection(section) {
        [loginSection, signupSection, uploadSection, registerAgrovetSection, registerExtensionWorkerSection].forEach(sec => sec.classList.add("d-none"));
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
            btnRegisterAgrovet.classList.remove("d-none");
            btnRegisterExtensionWorker.classList.remove("d-none");
            userGreeting.textContent = `Welcome, ${username || 'User'}!`;
        } else {
            uploadSection.classList.add("d-none");
            btnLogout.classList.add("d-none");
            btnLogin.classList.remove("d-none");
            btnSignup.classList.remove("d-none");
            btnRegisterAgrovet.classList.add("d-none");
            btnRegisterExtensionWorker.classList.add("d-none");
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

    btnRegisterAgrovet.addEventListener("click", function () {
        showSection(registerAgrovetSection);
        populateCountiesAndTowns("agrovet-county", "agrovet-town");
    });

    btnRegisterExtensionWorker.addEventListener("click", function () {
        showSection(registerExtensionWorkerSection);
        populateCountiesAndTowns("extension-worker-county", "extension-worker-town");
    });

    // Populate Counties and Towns Dropdowns
    async function populateCountiesAndTowns(countyId, townId) {
        try {
            const response = await fetch(`${backendBaseURL}/geolocation/counties`);
            if (!response.ok) {
                throw new Error("Failed to fetch counties");
            }
            const counties = await response.json();
            const countySelect = document.getElementById(countyId);
            const townSelect = document.getElementById(townId);

            // Clear existing options
            countySelect.innerHTML = "<option value=''>Select County</option>";
            townSelect.innerHTML = "<option value=''>Select Town</option>";

            // Populate county dropdown
            counties.forEach(county => {
                const option = document.createElement("option");
                option.value = county;
                option.textContent = county;
                countySelect.appendChild(option);
            });

            // Add event listener to county dropdown to populate town dropdown
            countySelect.addEventListener("change", async () => {
                const selectedCounty = countySelect.value;
                if (selectedCounty) {
                    const townResponse = await fetch(`${backendBaseURL}/geolocation/towns/${encodeURIComponent(selectedCounty)}`);
                    if (!townResponse.ok) {
                        throw new Error("Failed to fetch towns");
                    }
                    const towns = await townResponse.json();
                    townSelect.innerHTML = "<option value=''>Select Town</option>";
                    towns.forEach(town => {
                        const option = document.createElement("option");
                        option.value = town;
                        option.textContent = town;
                        townSelect.appendChild(option);
                    });
                } else {
                    townSelect.innerHTML = "<option value=''>Select Town</option>";
                }
            });
        } catch (error) {
            console.error("❌ Error populating counties and towns:", error);
            alert("Failed to load counties and towns. See console for details.");
        }
    }

    // Login Form Submission
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        let email = document.getElementById("loginEmail").value;
        let password = document.getElementById("loginPassword").value;
        try {
            let response = await fetch(`${backendBaseURL}/auth/login`, {
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
        let firstName = document.getElementById("signupFirstName").value;
        let lastName = document.getElementById("signupLastName").value;
        let username = document.getElementById("signupUsername").value;
        let email = document.getElementById("signupEmail").value;
        let password = document.getElementById("signupPassword").value;
        try {
            let response = await fetch(`${backendBaseURL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ first_name: firstName, last_name: lastName, username, email, password })
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
            let response = await fetch(`${backendBaseURL}/utils/treatments/${encodeURIComponent(disease)}`);
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
        } catch (error) {
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
            let response = await fetch(`${backendBaseURL}/upload`, {
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
            //Read the image file using FileReader
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
        
        // Fetch nearby agrovet shops and extension workers
        let nearbyAgrovets = item.nearby_agrovets || [];
        let nearbyExtensionWorkers = item.nearby_extension_workers || [];

        // Construct treatment HTML
        let treatmentHtml = `<a href="/treatment_page/${encodeURIComponent(item.disease)}" class="btn btn-info btn-sm">View Treatment</a>`;
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

    //wait for all rows to be processed
    await Promise.all(rowPromises);
    predictionsContainer.appendChild(table);
}

 // Agrovet Registration Form Submission
 registerAgrovetForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    let name = document.getElementById("agrovetName").value;
    let county = document.getElementById("agrovet-county").value;
    let town = document.getElementById("agrovet-town").value;
    let contact = document.getElementById("agrovetContact").value;

    if (!name || !county || !town || !contact) {
        alert("All fields are required");
        return;
    }

    try {
        let response = await fetch(`${backendBaseURL}/auth/register/agrovet`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, county, town, contact })
        });
        let data = await response.json();
        if (response.ok) {
            alert(data.message || "Agrovet registered successfully");
            registerAgrovetSection.classList.add("d-none");
            uploadSection.classList.remove("d-none");
        } else {
            alert(data.error || "Registration failed");
        }
    } catch (error) {
        console.error("❌ Agrovet Registration Error:", error);
        alert("Registration failed. See console for details.");
    }
});

    // Extension Worker Registration Form Submission
    registerExtensionWorkerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        let firstName = document.getElementById("extensionWorkerFirstName").value;
        let lastName = document.getElementById("extensionWorkerLastName").value;
        let services = document.getElementById("extensionWorkerServices").value.split(',').map(service => service.trim());
        let county = document.getElementById("extension-worker-county").value;
        let town = document.getElementById("extension-worker-town").value;
        let contact = document.getElementById("extensionWorkerContact").value;

        if (!firstName || !lastName || services.length === 0 || !county || !town || !contact) {
            alert("All fields are required");
            return;
        }

        try {
            let response = await fetch(`${backendBaseURL}/auth/register/extension-worker`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ first_name: firstName, last_name: lastName, services: services, county: county, town: town, contact: contact })
            });
            let data = await response.json();
            if (response.ok) {
                alert(data.message || "Extension worker registered successfully");
                registerExtensionWorkerSection.classList.add("d-none");
                uploadSection.classList.remove("d-none");
            } else {
                alert(data.error || "Registration failed");
            }
        } catch (error) {
            console.error("❌ Extension Worker Registration Error:", error);
            alert("Registration failed. See console for details.");
        }
    });

  // Check for stored JWT token on load
  if (localStorage.getItem("token")) {
    btnLogout.classList.remove("d-none");
    showSection(uploadSection);
  }
});