/**
 * SnapShop Notifications - Real-time SocketIO notification handler
 */
document.addEventListener('DOMContentLoaded', function () {
    // Check if socket.io is available
    if (typeof io === 'undefined') return;

    var socket = io();

    socket.on('connect', function () {
        console.log('Notifications connected');
    });

    // Listen for real-time notifications
    socket.on('new_notification', function (data) {
        var badge = document.getElementById('notification-badge');
        if (badge) {
            var count = parseInt(badge.textContent) || 0;
            badge.textContent = count + 1;
            badge.style.display = 'inline-block';
        }

        // Add notification to dropdown
        var list = document.getElementById('notification-list');
        if (list && data.message) {
            var item = document.createElement('li');
            item.className = 'list-group-item list-group-item-action';
            item.innerHTML = '<div class="d-flex"><div class="flex-grow-1"><p class="mb-0 small">' +
                data.message + '</p><small class="text-muted">Just now</small></div></div>';
            list.prepend(item);
        }
    });

    // Mark All as Read
    var markAllBtn = document.getElementById('mark-all-read');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', function () {
            fetch('/system/notifications/read', { method: 'POST' })
                .then(function () {
                    var badge = document.getElementById('notification-badge');
                    if (badge) {
                        badge.textContent = '0';
                        badge.style.display = 'none';
                    }
                });
        });
    }
});
