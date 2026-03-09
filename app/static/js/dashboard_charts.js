/**
 * Dashboard Charts - Top Selling Products & Revenue (Last 7 Days)
 * Uses Chart.js loaded from CDN in dashboard.html
 */
document.addEventListener('DOMContentLoaded', function () {
    var dataEl = document.getElementById('dashboard-data');
    if (!dataEl) return;

    var data;
    try {
        data = JSON.parse(dataEl.textContent);
    } catch (e) {
        console.error('Dashboard chart data parse error:', e);
        return;
    }

    // --- Top 5 Selling Products (Bar Chart) ---
    var topCtx = document.getElementById('topProductsChart');
    if (topCtx && data.top_products_labels && data.top_products_labels.length > 0) {
        new Chart(topCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: data.top_products_labels,
                datasets: [{
                    label: 'Units Sold',
                    data: data.top_products_data,
                    backgroundColor: [
                        'rgba(105, 108, 255, 0.85)',
                        'rgba(113, 221, 55, 0.85)',
                        'rgba(255, 171, 0, 0.85)',
                        'rgba(3, 195, 236, 0.85)',
                        'rgba(255, 62, 29, 0.85)'
                    ],
                    borderColor: [
                        '#696cff', '#71dd37', '#ffab00', '#03c3ec', '#ff3e1d'
                    ],
                    borderWidth: 2,
                    borderRadius: 6,
                    barThickness: 30
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, font: { size: 11 } },
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        ticks: { font: { size: 10 }, maxRotation: 45 },
                        grid: { display: false }
                    }
                }
            }
        });
    } else if (topCtx) {
        topCtx.parentNode.innerHTML = '<p class="text-muted text-center py-4">No sales data yet</p>';
    }

    // --- Revenue Last 7 Days (Line Chart) ---
    var revCtx = document.getElementById('revenueChart');
    if (revCtx && data.revenue_labels && data.revenue_labels.length > 0) {
        new Chart(revCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: data.revenue_labels,
                datasets: [{
                    label: 'Revenue (Rs.)',
                    data: data.revenue_data,
                    borderColor: '#696cff',
                    backgroundColor: 'rgba(105, 108, 255, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#696cff',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { font: { size: 11 }, callback: function (v) { return 'Rs. ' + v; } },
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        ticks: { font: { size: 11 } },
                        grid: { display: false }
                    }
                }
            }
        });
    } else if (revCtx) {
        revCtx.parentNode.innerHTML = '<p class="text-muted text-center py-4">No revenue data for the last 7 days</p>';
    }
});
