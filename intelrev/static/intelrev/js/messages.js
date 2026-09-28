document.addEventListener("DOMContentLoaded", function() {
  const form = document.getElementById("register-form");
  const username = form.querySelector("#id_username");
  const email = form.querySelector("#id_email");
  const password = form.querySelector("#id_password");
  const confirmPassword = form.querySelector("#id_confirm_password");
  const submitBtn = document.getElementById("register-btn");

  function showError(input, message) {
    input.classList.add("is-invalid");
    input.nextElementSibling.innerText = message;
  }

  function clearError(input) {
    input.classList.remove("is-invalid");
    input.nextElementSibling.innerText = "";
  }

  function validateFields() {
    let valid = true;

    // Username validation
    if (username.value.length < 3) {
      showError(username, "Username must be at least 3 characters");
      valid = false;
    } else {
      clearError(username);
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.value)) {
      showError(email, "Enter a valid email address");
      valid = false;
    } else {
      clearError(email);
    }

    // Password validation
    if (password.value.length < 6) {
      showError(password, "Password must be at least 6 characters");
      valid = false;
    } else {
      clearError(password);
    }

    // Confirm password validation
    if (password.value !== confirmPassword.value) {
      showError(confirmPassword, "Passwords do not match");
      valid = false;
    } else {
      clearError(confirmPassword);
    }

    // Enable submit button only if all fields valid
    submitBtn.disabled = !valid;
  }

  // Run validation on input
  username.addEventListener("input", validateFields);
  email.addEventListener("input", validateFields);
  password.addEventListener("input", validateFields);
  confirmPassword.addEventListener("input", validateFields);
});
