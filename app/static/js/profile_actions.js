document.addEventListener('DOMContentLoaded', () => {
    // Preview Image Logic
    const uploadInput = document.getElementById('upload');
    const uploadedAvatar = document.getElementById('uploadedAvatar');
    if (uploadInput && uploadedAvatar) {
        uploadInput.addEventListener('change', function (evt) {
            const [file] = this.files;
            if (file) {
                uploadedAvatar.src = URL.createObjectURL(file);
            }
        });
    }

    // Toggle Eye Function (Attach to global window if used inline)
    window.toggleEye = function (id, el) {
        const input = document.getElementById(id);
        const icon = el.querySelector('i');
        if (input && icon) {
            if (input.type === "password") {
                input.type = "text";
                icon.classList.replace('bx-hide', 'bx-show');
            } else {
                input.type = "password";
                icon.classList.replace('bx-show', 'bx-hide');
            }
        }
    };

    // Toggle Password Section Function
    window.togglePasswordSection = function () {
        const section = document.getElementById('passwordSection');
        const btn = document.getElementById('changePassBtn');
        const passInput = document.getElementById('password');
        const confirmInput = document.getElementById('confirm_password');
        const errorDiv = document.getElementById('passwordError');

        if (!section || !btn || !passInput || !confirmInput) return;

        if (section.style.display === "none") {
            section.style.display = "block";
            btn.innerHTML = '<i class="bx bx-x me-1"></i> Cancel Change';
            btn.classList.replace('btn-outline-danger', 'btn-danger');
            passInput.setAttribute('required', 'required');
            confirmInput.setAttribute('required', 'required');
        } else {
            section.style.display = "none";
            btn.innerHTML = 'Change Password';
            btn.classList.replace('btn-danger', 'btn-outline-danger');
            passInput.value = '';
            confirmInput.value = '';
            passInput.removeAttribute('required');
            confirmInput.removeAttribute('required');
            if (errorDiv) errorDiv.classList.add('d-none');
        }
    };

    // Real-time Validation Logic
    const passInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    const errorDiv = document.getElementById('passwordError');
    const profileForm = document.getElementById('profileForm');
    const submitBtn = profileForm ? profileForm.querySelector('button[type="submit"]') : null;

    function validatePasswords() {
        if (!passInput || !confirmInput || !errorDiv || !submitBtn) return;
        const pass = passInput.value;
        const confirm = confirmInput.value;

        // Only validate if confirm field has value
        if (confirm === "") {
            errorDiv.classList.add('d-none');
            confirmInput.classList.remove('is-invalid');
            submitBtn.disabled = false;
            return;
        }

        if (pass !== confirm) {
            errorDiv.classList.remove('d-none');
            confirmInput.classList.add('is-invalid');
            submitBtn.disabled = true;
        } else {
            errorDiv.classList.add('d-none');
            confirmInput.classList.remove('is-invalid');
            submitBtn.disabled = false;
        }
    }

    if (passInput && confirmInput) {
        passInput.addEventListener('input', validatePasswords);
        confirmInput.addEventListener('input', validatePasswords);
    }

    // Form Validation on Submit
    if (profileForm) {
        profileForm.addEventListener('submit', function (e) {
            if (passInput && confirmInput) {
                const pass = passInput.value;
                const confirm = confirmInput.value;

                if (pass !== "" && pass !== confirm) {
                    e.preventDefault();
                    if (errorDiv) errorDiv.classList.remove('d-none');
                    return false;
                }
            }
        });
    }
});
