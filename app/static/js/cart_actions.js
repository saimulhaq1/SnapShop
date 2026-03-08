function updateQuantity(productId, element) {
    const newQty = parseInt(element.value);

    // Prevent zero or negative values
    if (isNaN(newQty) || newQty < 1) {
        element.value = 1;
        return;
    }

    if (!window.CartApiConfig || !window.CartApiConfig.updateQtyUrl) {
        console.error("Cart API URL not configured.");
        return;
    }

    // Call the AJAX route we added to the controller
    fetch(window.CartApiConfig.updateQtyUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId, qty: newQty })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Automatically reloads the page to update the Grand Total and Subtotal
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Error updating quantity:', error);
        });
}
