/**
 * Generic function to handle status updates via Fetch API
 */
function updateStatus(url, id, newStatus, selectElement, errorMessage) {
    let formData = new FormData();
    formData.append('status', newStatus);

    fetch(url + id, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            if (response.ok) {
                selectElement.classList.add('border-success-flash');
                setTimeout(() => { location.reload(); }, 400);
            } else {
                alert(errorMessage || "Error: " + response.status);
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Connection lost. Status not saved.");
        });
}

/**
 * Page-Specific Wrappers
 */
function updateCustomerStatus(id, status, el) {
    updateStatus('/customers/edit/', id, status, el, "Failed to update customer.");
}

function changeCategoryStatus(id, status, el) {
    updateStatus('/category/update_status/', id, status, el, "Failed to update category.");
}

function updateAddressStatus(id, status, el) {
    updateStatus('/address/update_status/', id, status, el, "Failed to update address.");
}

function changeOrderStatus(id, status, el) {
    updateStatus('/order/update_status/', id, status, el, "Failed to update order.");
}

function changePaymentStatus(id, status, el) {
    updateStatus('/payment/update_status/', id, status, el, "Failed to update payment.");
}

/**
 * Bootstrap Form Validation
 */
(function () {
    'use strict'
    document.addEventListener('DOMContentLoaded', function () {
        var forms = document.querySelectorAll('.needs-validation')
        Array.prototype.slice.call(forms).forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        })
    })
})();

/**
 * Dashboard and Product Management Scripts
 */
const initDashboard = () => {
    // --- PART 1: PRODUCT PRICE, TAX & PROFIT CALCULATOR ---
    const buyInput = document.getElementById('buy_price');
    const saleInput = document.getElementById('sale_price');
    const taxSelect = document.getElementById('tax_id');
    const discInput = document.getElementById('discount');

    // Preview Elements
    const taxPreview = document.getElementById('tax_preview'); // New Tax-only preview
    const profitText = document.getElementById('profit_display');
    const finalText = document.getElementById('total_preview') || document.getElementById('final_display');

    if (saleInput && taxSelect) {
        const calculateProductPrice = () => {
            let buy = parseFloat(buyInput?.value) || 0;
            let sale = parseFloat(saleInput.value) || 0;
            let taxRate = parseFloat(taxSelect.options[taxSelect.selectedIndex]?.getAttribute('data-rate')) || 0;
            let discount = parseFloat(discInput?.value) || 0;

            // 1. Calculate Tax Separately
            let taxAmount = (sale * (taxRate / 100));
            let customerPaysBeforeDisc = sale + taxAmount;

            // 2. Calculate Final Price after optional discount
            let customerPaysFinal = customerPaysBeforeDisc * (1 - (discount / 100));
            let profit = customerPaysFinal - buy;

            // 3. Update UI Elements
            if (taxPreview) {
                taxPreview.innerText = "Rs. " + taxAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }
            if (finalText) {
                finalText.innerText = "Rs. " + customerPaysFinal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            }
            if (profitText) {
                profitText.innerText = "Rs. " + profit.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                profitText.className = profit >= 0 ? "fw-bold text-success" : "fw-bold text-danger";
            }
        };

        // Event Listeners for Live Calculation
        [buyInput, saleInput, taxSelect, discInput].forEach(el => {
            if (el) {
                el.addEventListener('input', calculateProductPrice);
                el.addEventListener('change', calculateProductPrice);
            }
        });

        calculateProductPrice();
    }

    // --- PART 2: CATEGORY DUPLICATE VALIDATION ---
    const catNameInput = document.getElementById('cat_name');
    const parentDropdown = document.querySelector('select[name="parent_cat_id"]');

    if (catNameInput && parentDropdown) {
        catNameInput.addEventListener('input', function () {
            const inputName = this.value.trim().toLowerCase();
            const options = Array.from(parentDropdown.options).map(opt =>
                opt.text.replace('↳', '').trim().toLowerCase()
            );

            if (options.includes(inputName)) {
                this.setCustomValidity("This category name already exists.");
                this.classList.add('is-invalid');
            } else {
                this.setCustomValidity("");
                this.classList.remove('is-invalid');
            }
        });
    }
};

// Start scripts when the page is ready
document.addEventListener('DOMContentLoaded', initDashboard);