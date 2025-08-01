// 🎉 Confetti celebration
window.celebrateConfetti = function () {
    confetti({
        particleCount: 120,
        spread: 90,
        origin: { y: 0.6 }
    });
};

// ❌ Close modal
window.closeModal = function () {
    document.getElementById("bookModal").style.display = "none";
};

// 📖 Show modal with book details
window.showModal = function (book) {
    const modal = document.getElementById("bookModal");
    const modalContent = document.querySelector(".modal-content");

    // 📝 Populate modal fields
    setText("modalTitle", book.title);
    setText("modalAuthor", book.author);
    setText("modalMood", book.mood || "N/A");
    setText("modalRating", book.rating !== null ? book.rating : "N/A");
    setText("modalReview", book.review || "No review available.");
    setText("modalDescription", book.description || "No description available.");

    // 🗑️ Set delete form action
    document.getElementById("deleteForm").action = `/delete/${book.id}`;


    // 🖼️ Cover image
    const thumbnail = book.thumbnail || "https://via.placeholder.com/120x180?text=No+Cover";
    document.getElementById("modalThumbnail").src = thumbnail;

    // 🎨 Mood accent color
    const moodColor = getMoodColor(book.mood);
    modalContent.style.borderLeft = `8px solid ${moodColor}`;

    // 📦 Show modal
    modal.style.display = "block";
};

// 🧠 Utility: Set text content safely
function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

// 🎨 Mood color mapping
function getMoodColor(mood) {
    const colors = {
        calm: "#A8DADC",
        intense: "#E63946",
        nostalgic: "#D8BFD8",
        whimsical: "#FFB6C1",
        chill: "#B0E0E6",
        uplifting: "#FFD700",
        dark: "#2F4F4F"
    };
    return colors[mood?.toLowerCase()] || "#ccc";
}

// 🖱️ Close modal if user clicks outside
window.onclick = function (event) {
    const modal = document.getElementById("bookModal");
    if (event.target === modal) {
        window.closeModal();
    }
};


