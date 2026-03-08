document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('checkoutForm');
    const codMethod = document.getElementById('cod');
    const walletMethod = document.getElementById('walletMethod');
    const cardMethod = document.getElementById('cardMethod');

    const walletSection = document.getElementById('walletInfoSection');
    const cardSection = document.getElementById('cardInfoSection');
    const walletInput = document.getElementById('walletInput');
    const cardInput = document.getElementById('cardInput');

    function updateView() {
        walletSection.style.display = 'none';
        cardSection.style.display = 'none';
        if (walletInput) walletInput.required = false;
        if (cardInput) cardInput.required = false;

        if (walletMethod && walletMethod.checked) {
            walletSection.style.display = 'block';
            if (walletInput) walletInput.required = true;
        } else if (cardMethod && cardMethod.checked) {
            cardSection.style.display = 'block';
            if (cardInput) cardInput.required = true;
        }
    }

    if (codMethod) codMethod.addEventListener('change', updateView);
    if (walletMethod) walletMethod.addEventListener('change', updateView);
    if (cardMethod) cardMethod.addEventListener('change', updateView);

    // Sync Address Title to hidden field on submit
    form.onsubmit = function () {
        const visibleTitle = document.getElementById('address_title_visible');
        const hiddenTitle = document.getElementById('address_title_hidden');
        if (visibleTitle && hiddenTitle) {
            hiddenTitle.value = visibleTitle.value || 'Home';
        }
    };

    updateView();
});
document.addEventListener('DOMContentLoaded', function () {
    const paymentSelect = document.getElementById('payment_type');
    const cardSection = document.getElementById('card_details_section');
    const walletSection = document.getElementById('wallet_details_section');

    if (paymentSelect) {
        paymentSelect.addEventListener('change', function () {
            // Reset visibility
            cardSection.style.display = 'none';
            walletSection.style.display = 'none';

            // Show relevant section
            if (this.value === 'Card') {
                cardSection.style.display = 'block';
            } else if (this.value === 'Wallet') {
                walletSection.style.display = 'block';
            }
        });
    }
});