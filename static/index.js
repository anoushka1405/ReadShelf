// Make these functions global so inline onclick can access them
window.celebrateConfetti = function() {
    confetti({ particleCount: 120, spread: 90, origin: { y: 0.6 } });
}

window.closeModal = function() {
    document.getElementById('bookModal').style.display = 'none';
}

window.showModal = function(book) {
    document.getElementById('modalTitle').textContent = book.title;
    document.getElementById('modalAuthor').textContent = book.author;
    document.getElementById('modalMood').textContent = book.mood || 'N/A';
    document.getElementById('modalRating').textContent = book.rating !== null ? book.rating : 'N/A';
    document.getElementById('modalReview').textContent = book.review || 'No review available.';
    document.getElementById('deleteForm').action = `/delete/${book.id}`;
    document.getElementById('bookModal').style.display = 'block';
}

// Close modal if user clicks outside modal content
window.onclick = function(event) {
    const modal = document.getElementById('bookModal');
    if (event.target === modal) {
        window.closeModal();
    }
}
