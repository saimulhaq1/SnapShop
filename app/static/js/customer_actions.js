/**
 * Customer Actions - Status toggle handler
 */
function updateCustomerStatus(customerId, newStatus, selectEl) {
    var originalValue = selectEl.getAttribute('data-original') || selectEl.querySelector('option[selected]')?.value;

    fetch(window.CustomerApiConfig.updateStatusUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_id: customerId, status: newStatus })
    })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (data.success) {
                // Update visual styling
                selectEl.className = 'form-select form-select-sm fw-bold';
                if (newStatus === 'ACTIVE') {
                    selectEl.classList.add('text-success', 'border-success');
                } else if (newStatus === 'BLOCKED') {
                    selectEl.classList.add('text-danger', 'border-danger');
                } else {
                    selectEl.classList.add('text-secondary', 'border-secondary');
                }
                selectEl.setAttribute('data-original', newStatus);
            } else {
                // Revert on failure
                selectEl.value = originalValue || 'ACTIVE';
                alert('Failed to update status.');
            }
        })
        .catch(function () {
            selectEl.value = originalValue || 'ACTIVE';
            alert('Network error. Status was not updated.');
        });
}

/**
 * Global Address Status toggle
 */
function updateAddressStatus(addressId, newStatus, selectEl) {
    var originalValue = selectEl.getAttribute('data-original') || selectEl.querySelector('option[selected]')?.value;
    var url = window.AddressApiConfig ? window.AddressApiConfig.updateStatusUrl : '/address/update-status';

    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address_id: addressId, status: newStatus })
    })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (data.success) {
                selectEl.className = 'form-select form-select-sm fw-bold';
                if (newStatus === 'ACTIVE') {
                    selectEl.classList.add('text-success', 'border-success');
                } else if (newStatus === 'BLOCKED') {
                    selectEl.classList.add('text-danger', 'border-danger');
                } else {
                    selectEl.classList.add('text-secondary', 'border-secondary');
                }
                selectEl.setAttribute('data-original', newStatus);
            } else {
                selectEl.value = originalValue || 'ACTIVE';
                alert('Failed to update address status.');
            }
        })
        .catch(function () {
            selectEl.value = originalValue || 'ACTIVE';
            alert('Network error. Address status was not updated.');
        });
}

/**
 * Payment Status toggle
 */
function changePaymentStatus(selectEl) {
    var originalValue = selectEl.getAttribute('data-original') || selectEl.querySelector('option[selected]')?.value;
    var url = selectEl.getAttribute('data-update-url');

    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: selectEl.value })
    })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (data.success) {
                selectEl.className = 'form-select form-select-sm fw-bold';
                if (selectEl.value === 'PAID') {
                    selectEl.classList.add('text-success', 'border-success');
                } else if (selectEl.value === 'FAILED') {
                    selectEl.classList.add('text-danger', 'border-danger');
                } else {
                    selectEl.classList.add('text-warning', 'border-warning');
                }
                selectEl.setAttribute('data-original', selectEl.value);
            } else {
                selectEl.value = originalValue || 'PENDING';
                alert('Failed to update payment status: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(function () {
            selectEl.value = originalValue || 'PENDING';
            alert('Network error. Payment status was not updated.');
        });
}
