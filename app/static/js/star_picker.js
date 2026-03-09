document.addEventListener('DOMContentLoaded', () => {
    const starPicker = document.getElementById('star-picker');
    const ratingInput = document.getElementById('rating_input');

    if (!starPicker || !ratingInput) return;

    const stars = starPicker.querySelectorAll('.star-btn');

    // Hover effects
    stars.forEach(star => {
        star.addEventListener('mouseenter', () => {
            const val = parseInt(star.getAttribute('data-value'));
            highlightStars(val);
        });

        star.addEventListener('mouseleave', () => {
            const currentVal = parseInt(ratingInput.value) || 0;
            highlightStars(currentVal);
        });

        // Click to set value
        star.addEventListener('click', () => {
            const val = parseInt(star.getAttribute('data-value'));
            ratingInput.value = val;
            highlightStars(val);
        });
    });

    function highlightStars(count) {
        stars.forEach(star => {
            const val = parseInt(star.getAttribute('data-value'));
            if (val <= count) {
                star.classList.replace('bx-star', 'bxs-star');
                star.classList.replace('text-muted', 'text-warning');
            } else {
                star.classList.replace('bxs-star', 'bx-star');
                star.classList.replace('text-warning', 'text-muted');
            }
        });
    }
});
