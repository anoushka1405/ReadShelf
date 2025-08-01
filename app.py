from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import init_db, add_book, get_all_books, save_blurb, get_latest_blurb, delete_book
from dotenv import load_dotenv
import sqlite3
import os
import json
import requests
import google.generativeai as genai


# 🌱 Environment Setup
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ Gemini API key not found. Blurb generation may fail.")
else:
    genai.configure(api_key=api_key)

DB_NAME = 'books.db'
app = Flask(__name__)

# ✨ Gemini Blurb Generator
def generate_blurb(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return "⚠️ Could not generate your literary vibe at this time. Please try again later."

# 📚 Routes

@app.route('/')
def index():
    selected_mood = request.args.get('mood')
    all_books = get_all_books()
    mood_config = load_mood_config()

    books = [book for book in all_books if book[3] == selected_mood] if selected_mood else all_books
    return render_template('index.html', books=books, mood_config=mood_config, selected_mood=selected_mood)

@app.route('/wishlist')
def wishlist():
    books = get_all_books(status='wishlist')
    mood_config = load_mood_config()
    return render_template('wishlist.html', books=books, mood_config=mood_config)

@app.route('/reading')
def currently_reading():
    books = get_all_books(status='reading')
    mood_config = load_mood_config()
    return render_template('reading.html', books=books, mood_config=mood_config)

def get_book_cover(title):
    # Try Google Books
    gb_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}"
    gb_response = requests.get(gb_url).json()
    try:
        return gb_response['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    except (KeyError, IndexError):
        pass

    # Fallback to Open Library
    ol_url = f"https://openlibrary.org/search.json?title={title}"
    ol_response = requests.get(ol_url).json()
    try:
        cover_id = ol_response['docs'][0]['cover_i']
        return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    except (KeyError, IndexError):
        return None

@app.route('/api/fetch-cover', methods=['POST'])
def fetch_cover():
    data = request.json
    title = data.get('title')
    cover_url = get_book_cover(title)
    return jsonify({'cover_url': cover_url})


@app.route("/add", methods=["GET", "POST"])
def add_book_route():
    if request.method == "POST":
        print("📘 Form submitted!") 
        status = request.form["status"]
        title = request.form["title"]
        author = request.form["author"]
        mood = request.form.get("mood")
        rating = request.form.get("rating")
        review = request.form.get("review")

        page_count = request.form.get("page_count")
        description = request.form.get("description")
        thumbnail = request.form.get("thumbnail")
        categories = request.form.get("categories")

        add_book(
            title=title,
            author=author,
            mood=mood,
            review=review,
            rating=rating,
            status=status,
            page_count=page_count,
            description=description,
            thumbnail=thumbnail,
            categories=categories
        )

        return redirect("/")

    # 👇 This ensures the dropdown is populated
    mood_config = load_mood_config()
    return render_template("add_book.html", mood_options=list(mood_config.keys()))


@app.route('/update_book/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    mood_config = load_mood_config()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == 'POST':
        mood = request.form.get('mood')
        rating = request.form.get('rating')
        rating = int(rating) if rating else None
        review = request.form.get('review')

        c.execute("UPDATE books SET mood=?, rating=?, review=?, status='read' WHERE id=?", 
                  (mood, rating, review, book_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    c.execute("SELECT id, title FROM books WHERE id=?", (book_id,))
    book = c.fetchone()
    conn.close()
    return render_template('update_book.html', book=book, mood_options=list(mood_config.keys()))

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book_route(book_id):
    delete_book(book_id)
    return redirect(url_for('index'))

@app.route('/mark_read/<int:book_id>', methods=['POST'])
def mark_read(book_id):
    conn = sqlite3.connect(books.db)
    c = conn.cursor()
    c.execute("UPDATE books SET status='read' WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('currently_reading'))

@app.route('/blurb')
def blurb():
    books = get_all_books()
    mood_config = load_mood_config()

    review_mood_pairs = [
        f"Mood: {book[3]}, Review: {book[4]}"
        for book in books
        if book[4] and len(book[4].strip()) > 0
    ]

    if not review_mood_pairs:
        return "📭 Not enough reviews to generate your vibe yet. Try adding a few books!"

    prompt = (
        "You are an insightful, poetic book analyst. Based on the following moods and reviews, "
        "summarize the reader’s literary personality in 2–3 short, poetic lines.\n\n" + "\n".join(review_mood_pairs)
    )

    blurb_text = generate_blurb(prompt)
    save_blurb(blurb_text)
    return render_template("blurb.html", blurb=blurb_text)

@app.route('/latest_blurb')
def latest_blurb():
    blurb = get_latest_blurb()
    return render_template("blurb.html", blurb=blurb) if blurb else "No saved blurb found."

@app.route('/pomodoro')
def pomodoro():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title FROM books WHERE status='reading' ORDER BY id DESC")
    books = c.fetchall()
    conn.close()
    return render_template("pomodoro.html", books=books)

# 🧠 Optional: Definition lookup (not stored)
@app.route('/define/<word>')
def define_word(word):
    try:
        res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        data = res.json()
        if isinstance(data, list):
            definition = data[0]['meanings'][0]['definitions'][0]['definition']
            return jsonify({'word': word, 'definition': definition})
        else:
            return jsonify({'error': 'Definition not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🔧 Utility
def load_mood_config():
    with open('mood_config.json') as f:
        return json.load(f)

# 🚀 App Entry
if __name__ == '__main__':
    init_db()
    print("Available routes:")
    print(app.url_map)
    app.run(debug=True, host='127.0.0.1', port=5000)
