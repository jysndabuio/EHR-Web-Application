// static/js/register.js

document.addEventListener("DOMContentLoaded", function() {
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm_password");
    const passwordStrengthText = document.getElementById("password-strength");
    const passwordMatchText = document.getElementById("password-match");

    passwordInput.addEventListener("input", validatePassword);
    confirmPasswordInput.addEventListener("input", validatePasswordMatch);

    // Function to validate password strength
    function validatePassword() {
        const password = passwordInput.value;
        let strength = "Weak";
        const regexUpperCase = /[A-Z]/;
        const regexNumber = /\d/;
        const regexLength = /.{8,}/;

        // Check strength conditions
        if (regexUpperCase.test(password) && regexNumber.test(password) && regexLength.test(password)) {
            strength = "Strong";
        } else if (regexUpperCase.test(password) || regexNumber.test(password) || regexLength.test(password)) {
            strength = "Medium";
        }

        // Display password strength
        passwordStrengthText.textContent = `Password strength: ${strength}`;
        passwordStrengthText.style.color = strength === "Strong" ? "green" : strength === "Medium" ? "orange" : "red";
    }

    // Function to validate password match
    function validatePasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (password === confirmPassword) {
            passwordMatchText.textContent = "Passwords match!";
            passwordMatchText.style.color = "green";
        } else {
            passwordMatchText.textContent = "Passwords do not match!";
            passwordMatchText.style.color = "red";
        }
    }
});
