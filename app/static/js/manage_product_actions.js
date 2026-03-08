document.addEventListener('DOMContentLoaded', () => {
    // --- Delivery Toggle Logic ---
    const deliveryToggle = document.getElementById('freeDeliveryToggle');
    const deliveryChargeSection = document.getElementById('deliveryChargeSection');
    const freeDeliveryBadge = document.getElementById('freeDeliveryBadge');
    const hiddenInput = document.getElementById('is_free_delivery_hidden');

    if (deliveryToggle) {
        deliveryToggle.addEventListener('change', function () {
            if (this.checked) {
                // Free delivery ON
                if (deliveryChargeSection) deliveryChargeSection.classList.add('d-none');
                if (freeDeliveryBadge) freeDeliveryBadge.classList.remove('d-none');
                if (hiddenInput) hiddenInput.value = '1';
            } else {
                // Free delivery OFF — show charge input
                if (deliveryChargeSection) deliveryChargeSection.classList.remove('d-none');
                if (freeDeliveryBadge) freeDeliveryBadge.classList.add('d-none');
                if (hiddenInput) hiddenInput.value = '0';
            }
        });
    }

    // --- Gallery Images Stateful Upload Logic ---
    const galleryInput = document.getElementById('additional_images');
    const galleryContainer = document.getElementById('gallery-preview-container');
    const deletedExistingInput = document.getElementById('deleted_existing_images');

    let selectedFiles = []; // Holds the File objects

    if (galleryInput) {
        galleryInput.addEventListener('change', function (e) {
            const files = Array.from(e.target.files);

            // Append new files to our state array ensuring no exact duplicates
            files.forEach(file => {
                if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                    selectedFiles.push(file);
                }
            });

            updateGalleryInput();
            renderGalleryPreviews();
        });
    }

    function updateGalleryInput() {
        if (!galleryInput) return;
        // DataTransfer API allows modifying the FileList of an input
        const dataTransfer = new DataTransfer();
        selectedFiles.forEach(file => dataTransfer.items.add(file));
        galleryInput.files = dataTransfer.files;
    }

    function renderGalleryPreviews() {
        if (!galleryContainer) return;
        // Remove only newly previewed elements, keeping the existing db ones intact
        const newFileElements = galleryContainer.querySelectorAll('.gallery-item-new');
        newFileElements.forEach(el => el.remove());

        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function (e) {
                const div = document.createElement('div');
                div.className = 'position-relative border rounded bg-white gallery-item-new';
                div.style.width = '80px';
                div.style.height = '80px';
                div.innerHTML = `
                    <img src="${e.target.result}" class="w-100 h-100" style="object-fit: cover; border-radius: 4px;">
                    <button type="button" class="btn btn-sm btn-danger position-absolute top-0 start-100 translate-middle rounded-circle p-0 d-flex align-items-center justify-content-center shadow" 
                            onclick="removeNewImage(${index})" style="width: 22px; height: 22px;" title="Remove selection">
                        <i class="bx bx-x" style="font-size: 14px;"></i>
                    </button>
                `;
                galleryContainer.appendChild(div);
            }
            reader.readAsDataURL(file);
        });
    }

    window.removeNewImage = function (index) {
        selectedFiles.splice(index, 1);
        updateGalleryInput();
        renderGalleryPreviews();
    };

    window.removeExistingImage = function (id) {
        if (!deletedExistingInput) return;
        const currentVals = deletedExistingInput.value ? deletedExistingInput.value.split(',') : [];
        if (!currentVals.includes(id.toString())) {
            currentVals.push(id);
            deletedExistingInput.value = currentVals.join(',');
        }
        const el = document.getElementById('existing-img-' + id);
        if (el) el.remove();
    };
});
