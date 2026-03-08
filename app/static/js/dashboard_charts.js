document.addEventListener("DOMContentLoaded", function () {
    const dataEl = document.getElementById('dashboard-data');
    if (!dataEl) return;
    const data = JSON.parse(dataEl.textContent);

    // --- Top 5 Selling Products Bar Chart ---
    const topProductsCanvas = document.getElementById('topProductsChart');
    if (topProductsCanvas) {
        const topProductsCtx = topProductsCanvas.getContext('2d');
        new Chart(topProductsCtx, {
            type: 'bar',
            data: {
                labels: data.top_products_labels,
                datasets: [{
                    label: 'Total Units Sold',
                    data: data.top_products_data,
                    backgroundColor: 'rgba(105, 108, 255, 0.7)',
                    borderColor: 'rgba(105, 108, 255, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // --- Revenue Line Chart (Last 7 Days) ---
    const revenueCanvas = document.getElementById('revenueChart');
    if (revenueCanvas) {
        const revenueCtx = revenueCanvas.getContext('2d');
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: data.revenue_labels,
                datasets: [{
                    label: 'Revenue (Rs)',
                    data: data.revenue_data,
                    backgroundColor: 'rgba(113, 221, 55, 0.2)',
                    borderColor: 'rgba(113, 221, 55, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: 'rgba(113, 221, 55, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
});
