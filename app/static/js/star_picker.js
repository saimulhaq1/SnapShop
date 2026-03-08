document.addEventListener('DOMContentLoaded', () => {
    // --- Star Picker Logic ---
    const stars = document.querySelectorAll('.star-btn');
    const ratingInput = document.getElementById('rating_input');

    if (stars.length > 0 && ratingInput) {
        stars.forEach(star => {
            star.addEventListener('click', function () {
                const val = parseInt(this.dataset.value);
                ratingInput.value = val;
                stars.forEach((s, i) => {
                    if (i < val) {
                        s.classList.replace('bx-star', 'bxs-star');
                        s.classList.add('text-warning');
                        s.classList.remove('text-muted');
                    } else {
                        s.classList.replace('bxs-star', 'bx-star');
                        s.classList.remove('text-warning');
                        s.classList.add('text-muted');
                    }
                });
            });
            star.addEventListener('mouseover', function () {
                const val = parseInt(this.dataset.value);
                stars.forEach((s, i) => {
                    s.classList.toggle('text-warning', i < val);
                });
            });
            star.addEventListener('mouseout', function () {
                const selected = parseInt(ratingInput.value) || 0;
                stars.forEach((s, i) => {
                    s.classList.toggle('text-warning', i < selected);
                });
            });
        });
    }
});
