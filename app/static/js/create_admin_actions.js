document.addEventListener('DOMContentLoaded', function () {
    const toggleButtons = document.querySelectorAll('.password-toggle-btn');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            if (!input || !icon) return;

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bx-hide', 'bx-show');
            } else {
                input.type = 'password';
                icon.classList.replace('bx-show', 'bx-hide');
            }
        });
    });
});
