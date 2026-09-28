// static/js/room.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".needs-validation");
  const submitBtn = form?.querySelector("button[type='submit']");
  const cancelBtn = form?.querySelector(".btn-outline-secondary");
  const roomTypeSelect = document.getElementById("room_type");
  const priceInput = document.getElementById("price");
  const roomNumberInput = document.getElementById("room_number");
  const deleteModal = document.getElementById('deleteRoomModal');
  const confirmBtn = document.getElementById('confirmDeleteRoomBtn');
  const imageInput = document.querySelector("input[name='room_image']");
  const imagePreview = document.getElementById("imagePreview");
  const imagePreviewContainer = document.getElementById("imagePreviewContainer");

  // Basic form validation and button feedback

  if (form) {
    form.addEventListener("submit", (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      else {
        // show temporary saving spinner
        if (submitBtn) {
          const originalText = submitBtn.textContent;
          submitBtn.disabled = true;
          submitBtn.innerHTML =
            '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
          setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
          }, 3000);
        }
      }
      form.classList.add("was-validated");
    });
  }


  // Cancel confirmation prompt

  if (cancelBtn) {
    cancelBtn.addEventListener("click", (event) => {
      const confirmCancel = confirm(
        "Are you sure you want to cancel? Unsaved changes will be lost."
      );
      if (!confirmCancel) {
        event.preventDefault();
      }
    });
  }


  // Auto-uppercase room numbers (ex: a101 → A101)

  if (roomNumberInput) {
    roomNumberInput.addEventListener("input", () => {
      let val = roomNumberInput.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
      roomNumberInput.value = val;
    });
  }


  // Auto-fill base price depending on room type

  const basePrices = {
    Single: 100.0,
    Double: 150.0,
    Deluxe: 200.0,
    Suite: 300.0,
  };

  if (roomTypeSelect && priceInput) {
    roomTypeSelect.addEventListener("change", () => {
      const selectedType = roomTypeSelect.value;
      if (basePrices[selectedType]) {
        priceInput.value = basePrices[selectedType].toFixed(2);
      }
    });
  }


  // Image preview before upload

  if (imageInput && imagePreview && imagePreviewContainer) {
    imageInput.addEventListener("change", (event) => {
      const file = event.target.files[0];
      if (file) {
        const previewURL = URL.createObjectURL(file);
        imagePreview.src = previewURL;
        imagePreviewContainer.style.display = "block";
      }
      else {
        imagePreview.src = "";
        imagePreviewContainer.style.display = "none";
      }
    });
  }

  if (deleteModal && confirmBtn) {
    deleteModal.addEventListener('show.bs.modal', function(event) {
      let button = event.relatedTarget;
      if (button) {
        let roomNumber = button.getAttribute('data-room-number');
        // Set delete URL dynamically
        confirmBtn.href = `/rooms/delete/${roomNumber}/`;
      }
    });
  }

});
