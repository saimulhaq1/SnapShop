document.addEventListener('DOMContentLoaded', function () {
    const adminSelect = document.getElementById('admin_select');
    if (adminSelect) {
        adminSelect.addEventListener('change', function () {
            const adminId = this.value;
            const deleteBtn = document.getElementById('deleteBtn');
            if (deleteBtn) deleteBtn.disabled = !adminId;

            if (!adminId) {
                document.querySelectorAll('#permForm input[type="checkbox"]').forEach(cb => cb.checked = false);
                return;
            }

            fetch(`/staff/get-permissions/${adminId}`)
                .then(response => response.json())
                .then(perms => {
                    document.querySelectorAll('#permForm input[type="checkbox"]').forEach(cb => cb.checked = false);

                    Object.keys(perms).forEach(key => {
                        const checkbox = document.querySelector(`input[name="${key}"]`);
                        if (checkbox && perms[key] === true) {
                            checkbox.checked = true;
                        }
                    });
                })
                .catch(error => console.error('Error fetching permissions:', error));
        });
    }
});

window.confirmDelete = function () {
    const select = document.getElementById('admin_select');
    if (!select) return;

    const adminId = select.value;
    const adminName = select.options[select.selectedIndex].text;
    if (confirm(`CRITICAL: Permanently delete account for: ${adminName}?`)) {
        const form = document.getElementById('deleteForm');
        if (form) {
            form.action = "/staff/delete-employee/" + adminId;
            form.submit();
        }
    }
};
