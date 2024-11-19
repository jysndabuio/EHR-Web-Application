document.addEventListener("DOMContentLoaded", function () {
  // Function to toggle edit mode globally
  function toggleGlobalEditMode() {
      // Select all fields with the 'editable-input' class
      const editableFields = document.querySelectorAll('.editable-input');

      // Toggle the disabled state of all editable fields
      editableFields.forEach(field => field.disabled = !field.disabled);

      // Toggle visibility of Save and Cancel buttons
      const saveButton = document.getElementById('save-button');
      const cancelButton = document.getElementById('cancel-button');
      const editButton = document.getElementById('edit-button');

      if (saveButton.style.display === 'none') {
          saveButton.style.display = 'inline';
          cancelButton.style.display = 'inline';
          editButton.style.display = 'none';
      } else {
          saveButton.style.display = 'none';
          cancelButton.style.display = 'none';
          editButton.style.display = 'inline';
      }
  }

  // Function to cancel changes (reloads the page)
  function cancelChanges() {
      window.location.reload(); // Reload the page to reset any unsaved changes
  }

  // Attach the toggleGlobalEditMode function to the global Edit button
  const editButton = document.getElementById('edit-button');
  editButton.addEventListener('click', toggleGlobalEditMode);

  // Attach the cancelChanges function to the global Cancel button
  const cancelButton = document.getElementById('cancel-button');
  cancelButton.addEventListener('click', cancelChanges);
});
