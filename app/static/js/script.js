/**
 * Global JavaScript for E-Commerce Admin & Storefront
 * Consolidates logic for:
 * - Authentication (Password toggle, Validation)
 * - Product Management (Live pricing, Image preview)
 * - Search UI (Dynamic inputs)
 * - Checkout (Payment method toggles, Input masking)
 * - Payment Ledger (Status updates)
 */

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // ==========================================
    // 1. GLOBAL BOOTSTRAP FORM VALIDATION
    // ==========================================
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // ==========================================
    // 2. AUTHENTICATION (Login/Register)
    // ==========================================
    // 1. Password Visibility Toggle (Scalable)
    // ==========================================
    const toggleBtns = document.querySelectorAll('.toggle-password');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const inputGroup = this.closest('.input-group');
            if (inputGroup) {
                const passwordInput = inputGroup.querySelector('.password-field');
                const icon = this.querySelector('i');
                if (passwordInput && icon) {
                    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordInput.setAttribute('type', type);
                    icon.classList.toggle('bx-show');
                    icon.classList.toggle('bx-hide');
                }
            }
        });
    });

    // ==========================================
    // 3. PRODUCT MANAGEMENT (Add/Edit Product)
    // ==========================================
    const calcTriggers = document.querySelectorAll('.calc-trigger');
    if (calcTriggers.length > 0) {
        const calculateProductPricing = () => {
            const buy = parseFloat(document.getElementById('buy_price')?.value) || 0;
            const sale = parseFloat(document.getElementById('sale_price')?.value) || 0;
            const discPercent = parseFloat(document.getElementById('discount')?.value) || 0;
            const taxSelect = document.getElementById('tax_id');
            const taxRate = parseFloat(taxSelect?.options[taxSelect.selectedIndex]?.dataset.rate) || 0;

            const discountedBase = sale * (1 - (discPercent / 100));
            const taxAmount = discountedBase * (taxRate / 100);
            const finalPrice = discountedBase + taxAmount;
            const profit = discountedBase - buy;

            const taxPreview = document.getElementById('tax_preview');
            const profitDisplay = document.getElementById('profit_display');
            const finalDisplay = document.getElementById('final_display');

            if (taxPreview) taxPreview.innerText = 'Rs. ' + taxAmount.toLocaleString(undefined, { minimumFractionDigits: 2 });
            if (finalDisplay) finalDisplay.innerText = 'Rs. ' + finalPrice.toLocaleString(undefined, { minimumFractionDigits: 2 });

            if (profitDisplay) {
                profitDisplay.innerText = 'Rs. ' + profit.toLocaleString(undefined, { minimumFractionDigits: 2 });
                if (profit < 0) {
                    profitDisplay.classList.remove('text-success');
                    profitDisplay.classList.add('text-danger');
                } else {
                    profitDisplay.classList.remove('text-danger');
                    profitDisplay.classList.add('text-success');
                }
            }
        };

        calcTriggers.forEach(el => el.addEventListener('input', calculateProductPricing));
        calculateProductPricing(); // Initial run
    }

    // Product Image Preview
    const imageInput = document.getElementById('image_file');
    if (imageInput) {
        imageInput.onchange = function () {
            const file = this.files[0];
            const fileNameDisplay = document.getElementById('file-name-display');
            const previewContainer = document.getElementById('preview-container');
            const previewImg = document.getElementById('preview-img');

            if (file && fileNameDisplay && previewContainer && previewImg) {
                fileNameDisplay.innerHTML = `<i class="bx bx-check-circle text-success"></i> Selected: <strong>${file.name}</strong>`;
                previewContainer.classList.remove('d-none');
                const reader = new FileReader();
                reader.onload = function (e) { previewImg.src = e.target.result; };
                reader.readAsDataURL(file);
            }
        };
    }

    // ==========================================
    // 4. PRODUCT SEARCH UI (List Page)
    // ==========================================
    const searchBySelect = document.getElementById('search_by');
    if (searchBySelect) {
        const updateSearchUI = () => {
            const searchBy = searchBySelect.value;
            const operatorDiv = document.getElementById('operator_div');
            const searchInput = document.getElementById('search_value');

            if (operatorDiv && searchInput) {
                if (searchBy === 'price') {
                    operatorDiv.style.display = 'block';
                    searchInput.type = 'number';
                    searchInput.placeholder = 'Enter numeric value...';
                } else {
                    operatorDiv.style.display = 'none';
                    searchInput.type = 'text';
                    searchInput.placeholder = 'Type to search...';
                }
            }
        };
        searchBySelect.addEventListener('change', updateSearchUI);
        updateSearchUI(); // Initial run
    }

    // ==========================================
    // 5. CHECKOUT PAGE (Payment Methods)
    // ==========================================
    const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
    if (paymentMethods.length > 0) {
        const walletSection = document.getElementById('walletInfoSection');
        const cardSection = document.getElementById('cardFields');

        // Group Inputs
        const getInputs = (ids) => ids.map(id => document.getElementById(id)).filter(el => el !== null);
        const walletInputs = getInputs(['walletInput', 'walletNameInput']);
        const cardInputs = getInputs(['cardInput', 'expiryInput', 'cvcInput', 'cardNameInput']);

        const togglePaymentFields = () => {
            const selectedRadio = document.querySelector('input[name="payment_method"]:checked');
            const selectedValue = selectedRadio ? selectedRadio.value : '';

            // Helper to toggle
            const setState = (section, inputs, show) => {
                if (section) section.style.display = show ? 'block' : 'none';
                inputs.forEach(input => {
                    input.required = show;
                    input.disabled = !show;
                });
            };

            // Reset All
            setState(walletSection, walletInputs, false);
            setState(cardSection, cardInputs, false);

            // Activate Selected
            if (selectedValue === 'Digital Wallet') {
                setState(walletSection, walletInputs, true);
            } else if (selectedValue === 'Card') {
                setState(cardSection, cardInputs, true);
            }
        };

        paymentMethods.forEach(radio => radio.addEventListener('change', togglePaymentFields));
        togglePaymentFields(); // Initial run

        // Input Masking Logic
        const cardInput = document.getElementById('cardInput');
        if (cardInput) {
            cardInput.addEventListener('input', function (e) {
                let value = e.target.value.replace(/\D/g, '');
                let formattedValue = '';
                for (let i = 0; i < value.length; i++) {
                    if (i > 0 && i % 4 === 0) formattedValue += '-';
                    formattedValue += value[i];
                }
                e.target.value = formattedValue.substring(0, 19);
            });
        }

        const expiryInput = document.getElementById('expiryInput');
        if (expiryInput) {
            expiryInput.addEventListener('input', function (e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length >= 2) {
                    e.target.value = value.substring(0, 2) + '/' + value.substring(2, 4);
                } else {
                    e.target.value = value;
                }
            });
        }
    }
});

// ==========================================
// 6. PAYMENT LEDGER (Admin Status Update)
// ==========================================
// This function needs to be global because it's called via onchange="changePaymentStatus(this)"
window.changePaymentStatus = function (element) {
    const newStatus = element.value;
    const url = element.dataset.updateUrl;
    const formData = new FormData();
    formData.append('status', newStatus);

    fetch(url, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                element.className = 'form-select form-select-sm fw-bold ';
                if (newStatus === 'PAID') element.classList.add('text-success', 'border-success');
                else if (newStatus === 'FAILED') element.classList.add('text-danger', 'border-danger');
                else element.classList.add('text-warning', 'border-warning');
            } else {
                alert('Update failed. Ensure you have proper permissions.');
            }
        })
        .catch(error => console.error('Error:', error));
};
