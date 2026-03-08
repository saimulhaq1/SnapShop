function openEditModal(id, name) {
    const modalEl = document.getElementById('editBrandModal');
    if (!modalEl) return;
    const modal = new bootstrap.Modal(modalEl);
    document.getElementById('edit_brand_name').value = name;

    if (window.ManageBrandConfig && window.ManageBrandConfig.editUrlTemplate) {
        document.getElementById('editBrandForm').action = window.ManageBrandConfig.editUrlTemplate.replace('0', id);
    }
    modal.show();
}
