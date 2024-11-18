// JavaScript for toggling Edit/Save/Cancel buttons and enabling/disabling fields
document.getElementById("edit-button").addEventListener("click", function() {
    var inputs = document.querySelectorAll("input, textarea, select"); // Select all form fields
    inputs.forEach(function(input) {
      input.disabled = false; // Enable all fields
    });
    
    document.getElementById("edit-button").style.display = "none"; // Hide Edit button
    document.getElementById("save-button").style.display = "inline"; // Show Save button
    document.getElementById("cancel-button").style.display = "inline"; // Show Cancel button
  });

  // Cancel editing
  document.getElementById("cancel-button").addEventListener("click", function() {
    var inputs = document.querySelectorAll("input, textarea, select"); // Select all form fields
    inputs.forEach(function(input) {
      input.disabled = true; // Disable fields
    });

    document.getElementById("edit-button").style.display = "inline"; // Show Edit button
    document.getElementById("save-button").style.display = "none"; // Hide Save button
    document.getElementById("cancel-button").style.display = "none"; // Hide Cancel button
  });