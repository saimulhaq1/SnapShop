window.updateCustomerStatus = function (customerId, newStatus, selectElement) {
    selectElement.style.opacity = '0.5';
    selectElement.disabled = true;

    if (!window.CustomerApiConfig || !window.CustomerApiConfig.updateStatusUrl) {
        console.error("Customer API URL not configured.");
        return;
    }

    fetch(window.CustomerApiConfig.updateStatusUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_id: customerId, status: newStatus }),
    })
        .then(response => response.json())
        .then(data => {
            selectElement.style.opacity = '1';
            selectElement.disabled = false;
            if (data.success) {
                selectElement.className = 'form-select form-select-sm fw-bold ';
                if (newStatus === 'ACTIVE') selectElement.classList.add('text-success', 'border-success');
                else if (newStatus === 'BLOCKED') selectElement.classList.add('text-danger', 'border-danger');
                else selectElement.classList.add('text-secondary', 'border-secondary');
            } else {
                alert("Error: " + (data.message || "Failed to update status."));
                window.location.reload();
            }
        })
        .catch(error => {
            alert("Server connection error.");
            window.location.reload();
        });
};
