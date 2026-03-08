function updateDiscountSymbol() {
    var typeEl = document.getElementById('discountType');
    var symbolEl = document.getElementById('discountSymbol');
    if (!typeEl || !symbolEl) return;

    if (typeEl.value === 'Percentage') {
        symbolEl.textContent = '%';
    } else {
        symbolEl.textContent = 'RS';
    }
}

document.addEventListener('DOMContentLoaded', updateDiscountSymbol);
