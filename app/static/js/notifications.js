document.addEventListener('DOMContentLoaded', () => {
    if (typeof io === 'undefined') return;
    const socket = io();

    // ─── Shared helpers ────────────────────────────────────────
    function updateBellCount(badgeId, headerId, increment) {
        const badge = document.getElementById(badgeId);
        const header = document.getElementById(headerId);
        if (badge) {
            let current = parseInt(badge.innerText || '0');
            current = Math.max(0, current + increment);
            badge.innerText = current;
            if (current > 0) badge.classList.remove('d-none');
            if (header) header.innerText = `${current} New`;
        }
    }

    function prependItem(listId, html) {
        const list = document.getElementById(listId);
        if (list) {
            const placeholder = list.querySelector('.text-muted');
            if (placeholder && placeholder.closest('li')) placeholder.closest('li').remove();
            list.insertAdjacentHTML('afterbegin', html);
        }
    }

    // ─── Admin Alerts ───────────────────────────────────────────
    socket.on('admin_alert', (data) => {
        if (!document.getElementById('adminNotifBadge')) return;

        updateBellCount('adminNotifBadge', 'adminNotifCount', 1);

        let icon = 'bx-cart text-success';
        if (data.type === 'REVIEW') icon = 'bx-comment-detail text-warning';
        if (data.type === 'SYSTEM') icon = 'bx-broadcast text-danger';

        let targetList = 'adminSystemNotifList';
        if (data.type === 'ORDER') targetList = 'adminNotifList';
        if (data.type === 'REVIEW') targetList = 'adminReviewNotifList';

        prependItem(targetList, `
            <li class="position-relative ping-anim">
                <a class="dropdown-item border-bottom py-2 pe-5" href="${data.link || '#'}">
                    <div class="d-flex align-items-start">
                        <div class="avatar me-2 flex-shrink-0">
                            <span class="avatar-initial rounded bg-label-secondary"><i class="bx ${icon}"></i></span>
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="mb-1 small fw-bold text-wrap text-dark">${data.title}</h6>
                            <p class="mb-0 small text-muted text-wrap">${data.message}</p>
                        </div>
                    </div>
                </a>
                <button type="button" class="btn-close position-absolute top-50 end-0 translate-middle-y me-3 delete-notif-btn"
                    data-id="new" aria-label="Close" style="font-size:0.65rem;z-index:10;"></button>
            </li>`);
    });

    // ─── Customer Alerts ────────────────────────────────────────
    socket.on('customer_alert', (data) => {
        if (!document.getElementById('custNotifBadge')) return;

        updateBellCount('custNotifBadge', null, 1);

        const iconMap = {
            'SALE': 'bx-broadcast text-danger',
            'ORDER_STATUS': 'bx-package text-primary',
            'PAYMENT_STATUS': 'bx-credit-card text-success'
        };
        const icon = iconMap[data.type] || 'bx-bell text-secondary';
        const targetList = (data.type === 'ORDER_STATUS' || data.type === 'PAYMENT_STATUS')
            ? 'custNotifList' : 'custSystemNotifList';

        prependItem(targetList, `
            <li class="position-relative ping-anim">
                <a class="dropdown-item border-bottom py-2 pe-5" href="${data.link || '#'}">
                    <div class="d-flex align-items-start">
                        <i class="bx ${icon} fs-4 me-2 mt-1"></i>
                        <div class="flex-grow-1">
                            <h6 class="mb-1 small fw-bold text-wrap text-dark">${data.title}</h6>
                            <p class="mb-0 small text-muted text-wrap">${data.message}</p>
                        </div>
                    </div>
                </a>
                <button type="button" class="btn-close position-absolute top-50 end-0 translate-middle-y me-3 delete-notif-btn"
                    data-id="new" aria-label="Close" style="font-size:0.65rem;z-index:10;"></button>
            </li>`);
    });

    // ─── Tab Memory (localStorage – survives page refresh) ─────
    const TAB_KEY = 'activeNotifTab';

    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(btn => {
        btn.addEventListener('shown.bs.tab', (e) => {
            localStorage.setItem(TAB_KEY, e.target.getAttribute('data-bs-target'));
        });
    });

    const savedTab = localStorage.getItem(TAB_KEY);
    if (savedTab) {
        const el = document.querySelector(`button[data-bs-target="${savedTab}"]`);
        if (el) new bootstrap.Tab(el).show();
    }

    // ─── Prevent Dropdown from closing on tab click ─────────────
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.addEventListener('click', (e) => {
            const tab = e.target.closest('[data-bs-toggle="tab"]');
            if (tab) {
                e.stopPropagation();
                e.preventDefault();
                new bootstrap.Tab(tab).show();
            }
        });
    });

    // ─── Mark as Read ───────────────────────────────────────────
    let hasMarkedRead = false;
    document.querySelectorAll('#adminNotifBell, #custNotifBell').forEach(bell => {
        bell.addEventListener('click', () => {
            if (hasMarkedRead) return;
            setTimeout(() => {
                fetch('/notifications/mark-read', {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                    .then(r => r.json())
                    .then(d => {
                        if (d.success) {
                            // Only hide the badge count, do NOT remove notification items
                            const badge = bell.querySelector('.badge');
                            if (badge) { badge.classList.add('d-none'); badge.innerText = '0'; }
                            const hdr = document.getElementById('adminNotifCount');
                            if (hdr) hdr.innerText = '0 New';
                            hasMarkedRead = true;
                        }
                    })
                    .catch(err => console.warn('mark-read error:', err));
            }, 1000);
        });
    });

    // ─── Delete / Dismiss ───────────────────────────────────────
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.delete-notif-btn');
        if (!btn) return;
        e.stopPropagation();
        const id = btn.getAttribute('data-id');
        const li = btn.closest('li');

        if (id === 'new') { if (li) li.remove(); return; }

        fetch(`/notifications/${id}/delete`, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(r => r.json())
            .then(d => { if (d.success && li) li.remove(); })
            .catch(err => console.warn('delete error:', err));
    });

});
