document.addEventListener("DOMContentLoaded", function () {
    // Navigation Buttons
    let btnLogin = document.getElementById("btn-login");
    let btnSignup = document.getElementById("btn-signup");
    let btnLogout = document.getElementById("btn-logout");

    // Sections
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

    // Validate DOM elements
    if (!btnLogin || !btnSignup || !btnLogout ||
        !loginSection || !signupSection || !uploadSection ||
        !loginForm || !signupForm || !uploadForm ||
        !fileInput || !buttonPredict || !loadingIndicator || !predictionsContainer || !userGreeting) {
        console.error("One or more required DOM elements are missing.");
        return;
    }

    // Authentication check
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

    // Button Event Listeners
    btnLogin.addEventListener("click", () => {
        loginSection.classList.remove("d-none");
        signupSection.classList.add("d-none");
        uploadSection.classList.add("d-none");
    });

    btnSignup.addEventListener("click", () => {
        signupSection.classList.remove("d-none");
        loginSection.classList.add("d-none");
        uploadSection.classList.add("d-none");
    });

    btnLogout.addEventListener("click", () => {
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
            let response = await fetch(`${window.location.origin}/auth/login`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({email, password})
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
            let response = await fetch(`${window.location.origin}/auth/register`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username, email, password})
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

    // Image Upload & Predictions
    uploadForm.addEventListener("submit", async (event) => {
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

    // Display predictions properly
    function displayPredictions(results, files) {
        predictionsContainer.innerHTML = "";
    
        let rows = new Array(results.length);
        let filesRead = 0;
    
        results.forEach((item, index) => {
            let reader = new FileReader();
            reader.onload = function (e) {
                let confidence = parseFloat(item.confidence).toFixed(2);
                let color = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : 'danger';
    
                rows[index] = `
                    <tr>
                        <td><img src="${e.target.result}" class="img-thumbnail" width="100"></td>
                        <td>${item.disease}</td>
                        <td class="text-${color}"><strong>${confidence}%</strong></td>
                    </tr>
                `;
    
                filesRead++;
                if (filesRead === results.length) {
                    // All images are processed — now render the table
                    let table = `
                        <table class="table table-striped table-bordered">
                            <thead class="table-dark">
                                <tr>
                                    <th>Image</th>
                                    <th>Diagnostic</th>
                                    <th>Confidence Interval</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows.join('')}
                            </tbody>
                        </table>
                    `;
                    predictionsContainer.innerHTML = table;
                }
            };
            reader.readAsDataURL(files[index]);
        });
    }      
});