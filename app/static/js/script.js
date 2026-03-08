/**
 * SnapShop - Main Script
 * Handles password toggles, sidebar interactions, advanced filters, brand dropdowns, and quantity controls
 */
document.addEventListener('DOMContentLoaded', function () {

    // --- Password Toggle ---
    document.querySelectorAll('.form-password-toggle i, .form-password-toggle .bx').forEach(function (el) {
        el.addEventListener('click', function (e) {
            e.preventDefault();
            var container = el.closest('.form-password-toggle') || el.closest('.input-group');
            if (!container) return;
            var input = container.querySelector('input');
            if (input.getAttribute('type') === 'password') {
                input.setAttribute('type', 'text');
                el.classList.remove('bx-hide');
                el.classList.add('bx-show');
            } else {
                input.setAttribute('type', 'password');
                el.classList.remove('bx-show');
                el.classList.add('bx-hide');
            }
        });
    });

    // --- Advanced Filter Toggle ---
    var toggleBtn = document.getElementById('toggleAdvancedFilter');
    var filterRow = document.getElementById('advancedFilterRow');
    if (toggleBtn && filterRow) {
        toggleBtn.addEventListener('click', function () {
            filterRow.classList.toggle('d-none');
            var icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.classList.toggle('bx-filter-alt');
                icon.classList.toggle('bx-x');
            }
        });
    }

    // --- Brand Dropdown (Select2-style or native) ---
    var brandSelect = document.getElementById('brand_id');
    if (brandSelect && typeof $.fn !== 'undefined' && typeof $.fn.select2 !== 'undefined') {
        $(brandSelect).select2({ placeholder: 'Select a brand', allowClear: true });
    }

    // --- Quantity Controls ---
    document.querySelectorAll('.qty-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var input = btn.closest('.input-group').querySelector('.qty-input');
            if (!input) return;
            var val = parseInt(input.value) || 1;
            if (btn.dataset.action === 'increase') {
                input.value = val + 1;
            } else if (btn.dataset.action === 'decrease' && val > 1) {
                input.value = val - 1;
            }
            input.dispatchEvent(new Event('change'));
        });
    });

    // --- Auto-dismiss flash messages ---
    document.querySelectorAll('.alert.auto-dismiss').forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

});
