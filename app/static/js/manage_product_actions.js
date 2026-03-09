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

                // Show preview
                var reader = new FileReader();
                reader.onload = function (e) {
                    if (previewImg) {
                        previewImg.src = e.target.result;
                    }
                    if (previewContainer) {
                        previewContainer.classList.remove('d-none');
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // === GALLERY IMAGES PREVIEW ===
    var additionalImages = document.getElementById('additional_images');
    var galleryContainer = document.getElementById('gallery-preview-container');

    if (additionalImages) {
        additionalImages.addEventListener('change', function () {
            // Remove previously-added new previews (keep existing server images)
            var oldPreviews = galleryContainer.querySelectorAll('.gallery-item-new');
            oldPreviews.forEach(function (el) { el.remove(); });

            if (this.files) {
                Array.from(this.files).forEach(function (file, index) {
                    var reader = new FileReader();
                    reader.onload = function (e) {
                        var wrapper = document.createElement('div');
                        wrapper.className = 'position-relative border rounded bg-white gallery-item-new';
                        wrapper.style.cssText = 'width: 80px; height: 80px;';
                        wrapper.id = 'new-img-' + index;

                        var img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'w-100 h-100';
                        img.style.cssText = 'object-fit: cover; border-radius: 4px;';

                        wrapper.appendChild(img);
                        galleryContainer.appendChild(wrapper);
                    };
                    reader.readAsDataURL(file);
                });
            }
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
