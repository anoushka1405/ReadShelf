console.log("✅ add_book.js loaded");

// ✅ Define toggleFields first
function toggleFields() {
    const status = document.getElementById("status").value;
    const moodField = document.getElementById("mood-field");
    const ratingField = document.getElementById("rating-field");
    const reviewField = document.getElementById("review-field");

    const isRead = status === "read";
    moodField.style.display = isRead ? "block" : "none";
    ratingField.style.display = isRead ? "block" : "none";
    reviewField.style.display = isRead ? "block" : "none";

    document.getElementById("mood").required = isRead;
    document.getElementById("rating").required = isRead;
}

document.addEventListener("DOMContentLoaded", function () {
    toggleFields(); // ✅ Safe to call now

    const titleInput = document.getElementById("titleInput");
    const authorInput = document.querySelector("input[name='author']");
    const pageCountInput = document.getElementById("page-count");
    const descriptionInput = document.getElementById("book-description");
    const thumbnailInput = document.getElementById("thumbnailInput");
    const categoriesInput = document.getElementById("book-categories");

    const coverPreview = document.getElementById("cover-preview");
    const coverImage = document.getElementById("cover-image");
    const goodreadsHelper = document.getElementById("goodreads-helper");
    const form = document.getElementById("addBookForm");
    const moodSelect = document.getElementById("mood");

    let debounceTimer;

    titleInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = titleInput.value.trim();
            if (query.length < 3) return;

            fetch(`https://www.googleapis.com/books/v1/volumes?q=intitle:${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.items && data.items.length > 0) {
                        const book = data.items[0].volumeInfo;
                        console.log("Fetched book data:", book); // 🐞 Debug

                        authorInput.value = Array.isArray(book.authors) ? book.authors.join(", ") : "Unknown Author";
                        pageCountInput.value = book.pageCount || "";
                        descriptionInput.value = book.description || "";
                        categoriesInput.value = Array.isArray(book.categories) ? book.categories.join(", ") : "";

                        const thumbnail = book.imageLinks?.thumbnail || "";
                        thumbnailInput.value = thumbnail;

                        if (thumbnail) {
                            coverImage.src = thumbnail;
                            coverPreview.style.display = "block";
                            goodreadsHelper.style.display = "none";
                        } else {
                            coverPreview.style.display = "none";

                            const searchURL = `https://www.goodreads.com/search?q=${encodeURIComponent(book.title + " " + (book.authors?.[0] || ""))}`;
                            goodreadsHelper.innerHTML = `
                                <a href="${searchURL}" target="_blank" rel="noopener noreferrer" class="goodreads-link">
                                    🔍 Find cover on Goodreads
                                </a>
                            `;
                            goodreadsHelper.style.display = "block";
                        }
                    }
                })
                .catch(err => console.error("Google Books API error:", err));
        }, 500);
    });

    thumbnailInput.addEventListener("input", () => {
        const url = thumbnailInput.value.trim();
        if (url && url.startsWith("http")) {
            coverImage.src = url;
            coverPreview.style.display = "block";
            goodreadsHelper.style.display = "none";
        } else {
            coverPreview.style.display = "none";
        }
    });

    const manualThumbnail = document.getElementById("manual-thumbnail");

manualThumbnail.addEventListener("input", () => {
    const url = manualThumbnail.value.trim();
    if (url && url.startsWith("http")) {
        thumbnailInput.value = url;
        coverImage.src = url;
        coverPreview.style.display = "block";
        goodreadsHelper.style.display = "none";
    } else {
        coverPreview.style.display = "none";
    }
});


    form.addEventListener("submit", function (event) {
        const title = titleInput.value.trim();
        const thumbnail = thumbnailInput.value.trim();
        const status = document.getElementById("status").value;
    
        let missingFields = [];
    
        if (!title) missingFields.push("Title");
        
        if (!thumbnail && status === "read") {
            missingFields.push("Thumbnail");
        }
        
    
        if (status === "read") {
            const mood = moodSelect.value;
            const rating = document.getElementById("rating").value;
    
            if (!mood) missingFields.push("Mood");
            if (!rating) missingFields.push("Rating");
        }
    
        if (missingFields.length > 0) {
            event.preventDefault();
            alert(`Please fill in the following fields before submitting:\n• ${missingFields.join("\n• ")}`);
        }
    });
    
});
