document.addEventListener('DOMContentLoaded', () => {

    /* ==========================================================
       1. PILLAR 6: STICKY HEADER ANIMATION
       ========================================================== */
    const header = document.getElementById('mainHeader');
    const spacer = document.getElementById('headerSpacer');

    window.addEventListener('scroll', () => {
        if (!header) return;
        if (window.scrollY > 50) {
            header.classList.add('position-fixed');
            header.classList.add('py-2');
            header.classList.remove('py-3');
            if (spacer) spacer.style.height = '85px'; // Adjust based on header height
        } else {
            header.classList.remove('position-fixed');
            header.classList.add('py-3');
            header.classList.remove('py-2');
            if (spacer) spacer.style.height = '0px';
        }
    });

    /* ==========================================================
       2. PILLAR 6: AJAX LIVE SEARCH
       ========================================================== */
    const searchInput = document.getElementById('search_value');
    const searchCat = document.getElementById('search_by');
    const resultsDiv = document.getElementById('searchResults');
    const resultsList = document.getElementById('searchResultsList');
    let debounceTimer;

    if (searchInput && resultsDiv && window.ProductApiConfig && window.ProductApiConfig.searchUrl) {
        searchInput.setAttribute('autocomplete', 'off'); // Prevent browser autocomplete blocking UI

        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();
            const categorySelect = searchCat ? searchCat.value : '';
            let catId = '';

            if (categorySelect.startsWith('cat_')) {
                catId = categorySelect.split('_')[1];
            }

            if (query.length < 2) {
                resultsDiv.classList.add('d-none');
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`${window.ProductApiConfig.searchUrl}?q=${encodeURIComponent(query)}&cat_id=${catId}`)
                    .then(r => r.json())
                    .then(data => {
                        resultsList.innerHTML = '';
                        if (data.length > 0) {
                            data.forEach(item => {
                                const a = document.createElement('a');
                                a.href = item.url;
                                a.className = "list-group-item list-group-item-action d-flex align-items-center py-2";
                                a.innerHTML = `
                                <img src="${item.image_url}" class="rounded border me-3" style="width: 45px; height: 45px; object-fit: cover;">
                                <div class="flex-grow-1">
                                    <h6 class="mb-0 text-dark fw-bold" style="font-size: 0.95rem;">${item.name}</h6>
                                    <small class="text-muted" style="font-size: 0.8rem;">${item.category}</small>
                                </div>
                                <span class="text-primary fw-bold">Rs. ${item.price}</span>
                            `;
                                resultsList.appendChild(a);
                            });
                            resultsDiv.classList.remove('d-none');
                        } else {
                            resultsList.innerHTML = `<div class="p-3 text-center text-muted">No products found for '<strong>${query}</strong>'</div>`;
                            resultsDiv.classList.remove('d-none');
                        }
                    })
                    .catch(e => console.error("AJAX Search failed: ", e));
            }, 300); // 300ms debounce
        });

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !resultsDiv.contains(e.target)) {
                resultsDiv.classList.add('d-none');
            }
        });

        // Ensure results reappear if clicking back into input with text
        searchInput.addEventListener('focus', (e) => {
            if (e.target.value.trim().length >= 2 && resultsList.innerHTML.trim() !== '') {
                resultsDiv.classList.remove('d-none');
            }
        });
    }

    /* ==========================================================
       3. PILLAR 6: QUICK VIEW MODAL
       ========================================================== */
    const quickViewButtons = document.querySelectorAll('.btn-quick-view');
    const qvModalEl = document.getElementById('quickViewModal');
    let qvModal;

    if (qvModalEl) {
        qvModal = new bootstrap.Modal(qvModalEl);
    }

    quickViewButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const productId = this.getAttribute('data-product-id');

            // Show a loading state if desired, then fetch
            fetch(`/api/product/${productId}`)
                .then(response => response.json())
                .then(data => {
                    // Populate Modal Content
                    document.getElementById('qvImage').src = data.image_url;
                    document.getElementById('qvArt').textContent = `ART: ${data.code}`;
                    document.getElementById('qvName').textContent = data.name;
                    document.getElementById('qvDescription').textContent = data.description;

                    // Price Logic
                    document.getElementById('qvPrice').textContent = `Rs. ${data.final_price}`;
                    const origPriceEl = document.getElementById('qvOriginalPrice');
                    const discBadgeEl = document.getElementById('qvDiscountBadge');

                    if (data.has_discount) {
                        origPriceEl.textContent = `Rs. ${data.original_price}`;
                        origPriceEl.classList.remove('d-none');
                        discBadgeEl.textContent = `${data.discount_percent}% OFF`;
                        discBadgeEl.classList.remove('d-none');
                    } else {
                        origPriceEl.classList.add('d-none');
                        discBadgeEl.classList.add('d-none');
                    }

                    // Stock Status
                    const stockStatusEl = document.getElementById('qvStockStatus');
                    const addToCartBtn = document.getElementById('qvAddToCartBtn');

                    if (data.is_out_of_stock) {
                        stockStatusEl.innerHTML = `<span class="badge bg-label-danger"><i class="bx bx-x-circle me-1"></i> Out of Stock</span>`;
                        addToCartBtn.classList.add('disabled');
                    } else {
                        stockStatusEl.innerHTML = `<span class="badge bg-label-success"><i class="bx bx-check-circle me-1"></i> In Stock (${data.stock} units)</span>`;
                        addToCartBtn.classList.remove('disabled');
                    }

                    // Action URLs
                    addToCartBtn.href = data.add_to_cart_url;
                    document.getElementById('qvViewFullBtn').href = data.url;

                    // Trigger Modal
                    qvModal.show();
                })
                .catch(err => {
                    console.error('Failed to load Quick View Data', err);
                });
        });
    });

});
