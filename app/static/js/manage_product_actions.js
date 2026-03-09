/**
 * Manage Product Actions
 * Handles: image preview, gallery preview, tax calculation, existing image removal
 */
document.addEventListener('DOMContentLoaded', function () {

    // === PRIMARY IMAGE PREVIEW ===
    var imageFile = document.getElementById('image_file');
    var previewContainer = document.getElementById('preview-container');
    var previewImg = document.getElementById('preview-img');
    var fileNameDisplay = document.getElementById('file-name-display');

    if (imageFile) {
        imageFile.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                var file = this.files[0];

                // Update filename display
                if (fileNameDisplay) {
                    fileNameDisplay.textContent = file.name;
                    fileNameDisplay.classList.remove('text-muted');
                    fileNameDisplay.classList.add('text-primary');
                }

                // Show preview with remove button
                var reader = new FileReader();
                reader.onload = function (e) {
                    if (previewImg) {
                        previewImg.src = e.target.result;
                    }
                    if (previewContainer) {
                        previewContainer.classList.remove('d-none');
                        // Add remove button if not already present
                        if (!previewContainer.querySelector('.preview-remove-btn')) {
                            var removeBtn = document.createElement('button');
                            removeBtn.type = 'button';
                            removeBtn.className = 'btn btn-sm btn-outline-danger mt-2 preview-remove-btn';
                            removeBtn.innerHTML = '<i class="bx bx-trash me-1"></i>Remove';
                            removeBtn.addEventListener('click', function () {
                                imageFile.value = '';
                                previewContainer.classList.add('d-none');
                                previewImg.src = '';
                                if (fileNameDisplay) {
                                    fileNameDisplay.textContent = 'No file chosen';
                                    fileNameDisplay.classList.remove('text-primary');
                                    fileNameDisplay.classList.add('text-muted');
                                }
                                removeBtn.remove();
                            });
                            previewContainer.appendChild(removeBtn);
                        }
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // === GALLERY IMAGES PREVIEW (With Individual Removal Tracking) ===
    var additionalImages = document.getElementById('additional_images');
    var galleryContainer = document.getElementById('gallery-preview-container');
    // We use a DataTransfer object to hold the current batch of files so we can remove individual ones.
    var currentGalleryFiles = new DataTransfer();

    if (additionalImages) {
        additionalImages.addEventListener('change', function () {
            // Append newly selected files to our DataTransfer object
            if (this.files) {
                Array.from(this.files).forEach(function (file) {
                    currentGalleryFiles.items.add(file);
                });
            }

            // Sync the input state
            this.files = currentGalleryFiles.files;

            // Re-render previews
            renderGalleryPreviews();
        });
    }

    function renderGalleryPreviews() {
        // Clear all currently displayed *new* previews
        var oldPreviews = galleryContainer.querySelectorAll('.gallery-item-new');
        oldPreviews.forEach(function (el) { el.remove(); });

        Array.from(currentGalleryFiles.files).forEach(function (file, index) {
            var reader = new FileReader();
            reader.onload = function (e) {
                var wrapper = document.createElement('div');
                wrapper.className = 'position-relative border rounded bg-white gallery-item-new shadow-sm';
                wrapper.style.cssText = 'width: 80px; height: 80px;';

                var img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'w-100 h-100';
                img.style.cssText = 'object-fit: cover; border-radius: 4px;';

                var removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'btn btn-sm btn-danger position-absolute top-0 start-100 translate-middle rounded-circle p-0 d-flex align-items-center justify-content-center shadow';
                removeBtn.style.cssText = 'width: 22px; height: 22px; z-index: 10;';
                // Add the X icon inside the button
                removeBtn.innerHTML = '<i class="bx bx-x" style="font-size: 14px;"></i>';

                removeBtn.addEventListener('click', function (evt) {
                    evt.preventDefault();
                    // Rebuild the DataTransfer object without this specific file
                    var newDt = new DataTransfer();
                    Array.from(currentGalleryFiles.files).forEach(function (f, i) {
                        if (i !== index) newDt.items.add(f);
                    });
                    currentGalleryFiles = newDt;
                    if (additionalImages) additionalImages.files = currentGalleryFiles.files;
                    renderGalleryPreviews();
                });

                wrapper.appendChild(img);
                wrapper.appendChild(removeBtn);
                galleryContainer.appendChild(wrapper);
            };
            reader.readAsDataURL(file);
        });
    }

    // === TAX PREVIEW (real-time GST calculation) ===
    var salePriceInput = document.querySelector('input[name="sale_price"]');
    var taxPreview = document.getElementById('tax_preview');

    if (salePriceInput && taxPreview) {
        function updateTaxPreview() {
            var price = parseFloat(salePriceInput.value) || 0;
            var gst = price * 0.05; // 5% GST
            taxPreview.textContent = 'Rs. ' + gst.toFixed(2);
        }
        salePriceInput.addEventListener('input', updateTaxPreview);
        updateTaxPreview(); // Run once on load
    }
});

/**
 * Remove an existing gallery image (marks it for deletion on submit)
 */
function removeExistingImage(imageId) {
    var el = document.getElementById('existing-img-' + imageId);
    if (el) {
        el.style.transition = 'opacity 0.3s';
        el.style.opacity = '0';
        setTimeout(function () { el.remove(); }, 300);
    }

    // Add this ID to the hidden field so the backend knows to delete it
    var hiddenField = document.getElementById('deleted_existing_images');
    if (hiddenField) {
        var current = hiddenField.value;
        hiddenField.value = current ? current + ',' + imageId : imageId;
    }
}
