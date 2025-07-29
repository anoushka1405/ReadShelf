function toggleFields() {
    const status = document.getElementById("status").value;
    const moodField = document.getElementById("mood-field");
    const ratingField = document.getElementById("rating-field");
    const reviewField = document.getElementById("review-field");

    if (status === "read") {
        moodField.style.display = "block";
        ratingField.style.display = "block";
        reviewField.style.display = "block";

        document.getElementById("mood").required = true;
        document.getElementById("rating").required = true;
    } else {
        moodField.style.display = "none";
        ratingField.style.display = "none";
        reviewField.style.display = "none";

        document.getElementById("mood").required = false;
        document.getElementById("rating").required = false;
    }
}

window.onload = toggleFields;
