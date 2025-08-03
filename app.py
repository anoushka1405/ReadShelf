from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from models import init_db, add_book, get_all_books, save_blurb, get_latest_blurb, delete_book
from readbot import generate_readbot_reply
from dotenv import load_dotenv
from collections import Counter, defaultdict
import sqlite3
import os
import json
import requests
import google.generativeai as genai
from weasyprint import HTML, CSS
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-GUI rendering
from io import BytesIO
import matplotlib.pyplot as plt
import base64


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

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    book_title = data['book_title']
    progress_info = data['progress_info']  # can be "Chapter 7", "Page 150", etc.

    reply = generate_readbot_reply(message, book_title, progress_info)
    return jsonify({'response': reply})

@app.route('/readbot', methods=['POST'])
def readbot_reply():
    data = request.get_json()
    user_message = data.get('message')
    book_title = data.get('bookTitle')
    user_progress = data.get('userProgress')

    try:
        from readbot import generate_readbot_reply
        bot_reply = generate_readbot_reply(user_message, book_title, user_progress)
        return jsonify({'reply': bot_reply})
    except Exception as e:
        print(f"[ReadBot Error]: {e}")
        return jsonify({'reply': "Hmm... I’m having trouble thinking right now. Mind trying again?"})

from collections import Counter, defaultdict

@app.route('/stats')
def stats():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE status = 'read'")
    books = [dict(row) for row in c.fetchall()]
    conn.close()

    total_books = len(books)
    ratings = [b['rating'] for b in books if b.get('rating') is not None]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0

    moods = [b['mood'] for b in books if b.get('mood')]
    mood_counts = Counter(moods)
    most_common_mood = mood_counts.most_common(1)[0][0] if mood_counts else "None"

    top_books = sorted(
        [b for b in books if b.get('rating') is not None],
        key=lambda b: b['rating'],
        reverse=True
    )[:3]

    mood_books = {}
    for mood in mood_counts:
        mood_books[mood] = [b for b in books if b.get('mood') == mood]

    # ✅ NEW: Calculate average rating per mood
    mood_rating_sums = defaultdict(float)
    mood_rating_counts = defaultdict(int)

    for b in books:
        if b.get('mood') and b.get('rating') is not None:
            mood_rating_sums[b['mood']] += b['rating']
            mood_rating_counts[b['mood']] += 1

    avg_rating_by_mood = {
        mood: round(mood_rating_sums[mood] / mood_rating_counts[mood], 2)
        for mood in mood_rating_sums
    }

    # ✅ NEW: Calculate number of books per rating
    books_per_rating = Counter([b['rating'] for b in books if b.get('rating') is not None])

    return render_template(
    'stats.html',
    total_books=total_books,
    avg_rating=avg_rating,
    most_common_mood=most_common_mood,
    top_books=top_books,
    mood_counts=mood_counts,
    mood_books=mood_books,
    avg_rating_by_mood=avg_rating_by_mood,
    books_per_rating=books_per_rating,
    mood_colors={
        "Calm": "#aee1f9",
        "Intense": "#ff6b6b",
        "Nostalgic": "#d8a47f",
        "Whimsical": "#cdb4db",
        "Chill": "#d0f4f7",
        "Uplifting": "#fff4b2",
        "Dark": "#999999"
    }  
)

@app.route('/export-pdf')
def export_pdf():
    def plot_to_base64(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return img_base64

    # Fetch books from DB
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM books ORDER BY id DESC")
    books = [dict(row) for row in c.fetchall()]
    conn.close()

    # Fix cover URLs to be absolute
    for b in books:
        if b.get('cover_url') and not b['cover_url'].startswith(('http://', 'https://')):
            b['cover_url'] = request.host_url.rstrip('/') + b['cover_url']

    # Prepare chart data
    moods = [b['mood'] for b in books if b.get('mood')]
    mood_counts = Counter(moods)

    mood_rating_sums = defaultdict(float)
    mood_rating_counts = defaultdict(int)
    for b in books:
        mood = b.get('mood')
        rating = b.get('rating')
        if mood and rating is not None:
            try:
                rating_val = float(rating)
                mood_rating_sums[mood] += rating_val
                mood_rating_counts[mood] += 1
            except ValueError:
                continue

    avg_rating_by_mood = {
        mood: round(mood_rating_sums[mood] / mood_rating_counts[mood], 2)
        for mood in mood_rating_sums if mood_rating_counts[mood] > 0
    }

    books_per_rating = Counter()
    for b in books:
        rating = b.get('rating')
        if rating is not None:
            try:
                rating_val = str(float(rating))
                books_per_rating[rating_val] += 1
            except ValueError:
                continue

    # Generate matplotlib charts as base64
    fig1, ax1 = plt.subplots()
    ax1.pie(mood_counts.values(), labels=mood_counts.keys(), autopct='%1.1f%%', startangle=90)
    ax1.set_title("Books by Mood")
    pie_chart = plot_to_base64(fig1)

    fig2, ax2 = plt.subplots()
    ax2.bar(avg_rating_by_mood.keys(), avg_rating_by_mood.values(), color="#88c")
    ax2.set_title("Average Rating by Mood")
    ax2.set_ylabel("Rating")
    bar_chart = plot_to_base64(fig2)

    fig3, ax3 = plt.subplots()
    ax3.bar(books_per_rating.keys(), books_per_rating.values(), color="#f99")
    ax3.set_title("Books by Rating")
    ax3.set_ylabel("Count")
    rating_chart = plot_to_base64(fig3)

    mood_colors = {
        "Calm": "#aee1f9",
        "Intense": "#ff6b6b",
        "Nostalgic": "#d8a47f",
        "Whimsical": "#cdb4db",
        "Chill": "#d0f4f7",
        "Uplifting": "#fff4b2",
        "Dark": "#999999"
    }

    # Render the export template with charts and books
    rendered = render_template(
        'export.html',
        books=books,
        mood_counts=mood_counts,
        avg_rating_by_mood=avg_rating_by_mood,
        books_per_rating=books_per_rating,
        mood_colors=mood_colors,
        pie_chart=pie_chart,
        bar_chart=bar_chart,
        rating_chart=rating_chart
    )

    # Convert to PDF with CSS
    css_path = os.path.join(app.root_path, 'static', 'style.css')
    css = CSS(filename=css_path)
    pdf = HTML(string=rendered, base_url=request.base_url).write_pdf(stylesheets=[css])

    # Send PDF as response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=readshelf_export.pdf'
    return response

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
