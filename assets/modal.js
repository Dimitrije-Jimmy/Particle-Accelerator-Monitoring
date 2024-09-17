/*
document.addEventListener('DOMContentLoaded', function () {
    const modalContent = document.getElementById('markdown-container');
    if (modalContent) {
        modalContent.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    }
});
*/

document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('markdown');
    const modalContent = document.getElementById('markdown-container');
    if (modal && modalContent) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                // Clicked on modal background; allow event to propagate
            } else {
                // Clicked inside modal content; prevent propagation
                e.stopPropagation();
            }
        });
    }
});

