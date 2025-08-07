function showReadingModal(book) {
  const modal = document.getElementById('readingModal');
  modal.style.display = 'block';

  // Set book details in modal
  document.getElementById('readingModalTitle').textContent = book.title;
  document.getElementById('readingModalAuthor').textContent = book.author;
  document.getElementById('readingModalDescription').textContent = book.description || 'No description available.';
  document.getElementById('readingModalThumbnail').src = book.thumbnail || '';
  document.getElementById('readingModalThumbnail').style.display = book.thumbnail ? 'block' : 'none';

  // Set delete form action
  const deleteForm = document.getElementById('deleteReadingForm');
  deleteForm.action = `/delete/${book.id}`;

  // Set mark as read form action
  const updateLink = document.getElementById('updateBookLink');
  updateLink.href = `/update_book/${book.id}`;

}

function closeReadingModal() {
  document.getElementById('readingModal').style.display = 'none';
}

// Optional: Close modal when clicking outside
window.addEventListener('click', function (event) {
  const modal = document.getElementById('readingModal');
  if (event.target === modal) {
    closeReadingModal();
  }
});

// Optional: Confetti effect on mark-read click (if using .mark-read-link)
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('.mark-read-link').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      confetti({
        particleCount: 150,
        spread: 70,
        origin: { y: 0.6 },
      });
      setTimeout(() => {
        window.location.href = this.dataset.href;
      }, 1000);
    });
  });
});

