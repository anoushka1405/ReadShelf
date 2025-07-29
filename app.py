from flask import Flask, render_template
from flask import request, redirect, url_for
from models import init_db, add_book, get_all_books
from dotenv import load_dotenv
from models import save_blurb, get_latest_blurb
import sqlite3


import os
import json

import google.generativeai as genai

load_dotenv()

# Load your Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # or paste your key directly
print("Loaded API key:", os.getenv("GEMINI_API_KEY"))

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

DB_NAME = 'books.db'

def generate_blurb(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return "⚠️ Could not generate your literary vibe at this time. Please try again later."



app = Flask(__name__)

@app.route('/')
def index():
    selected_mood = request.args.get('mood')
    all_books = get_all_books()
    mood_config = load_mood_config()

    if selected_mood:
        books = [book for book in all_books if book[3] == selected_mood]
    else:
        books = all_books

    return render_template('index.html',
                           books=books,
                           mood_config=mood_config,
                           selected_mood=selected_mood)
    

@app.route('/wishlist')
def wishlist():
    books = get_all_books(status='wishlist')
    mood_config = load_mood_config()
    return render_template('wishlist.html', books=books, mood_config=mood_config)


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

    review_text = "\n".join(review_mood_pairs)
    prompt = (
        "You are an insightful, poetic book analyst. Based on the following moods and reviews, "
        "summarize the reader’s literary personality in 2–3 short, poetic lines.\n\n" + review_text
    )

    blurb_text = generate_blurb(prompt)

    save_blurb(blurb_text)  # 💾 Save to database

    return render_template("blurb.html", blurb=blurb_text)

@app.route('/latest_blurb')
def latest_blurb():
    blurb = get_latest_blurb()
    if blurb:
        return render_template("blurb.html", blurb=blurb)
    return "No saved blurb found."



@app.route('/add', methods=['GET', 'POST'])
def add():
    mood_config = load_mood_config()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        status = request.form['status']

        # Optional fields
        mood = request.form.get('mood') if status == 'read' else None
        rating = request.form.get('rating')
        rating = int(rating) if (rating and status == 'read') else None
        review = request.form.get('review') if status == 'read' else None

        add_book(title, author, mood, review, rating, status)
        return redirect(url_for('index'))

    return render_template('add_book.html', mood_options=list(mood_config.keys()))

@app.route("/pomodoro")
def pomodoro():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT id, title FROM books WHERE status='reading' ORDER BY id DESC")
    books = c.fetchall()
    conn.close()
    return render_template("pomodoro.html", books=books)






def load_mood_config():
    with open('mood_config.json') as f:
        return json.load(f)
    
@app.route('/reading')
def currently_reading():
    books = get_all_books(status='reading')
    mood_config = load_mood_config()
    return render_template('reading.html', books=books, mood_config=mood_config)

@app.route('/mark_read/<int:book_id>', methods=['POST'])
def mark_read(book_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE books SET status='read' WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('currently_reading'))

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

    # GET request - fetch current book details
    c.execute("SELECT id, title FROM books WHERE id=?", (book_id,))
    book = c.fetchone()
    conn.close()

    return render_template('update_book.html', book=book, mood_options=list(mood_config.keys()))

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book_route(book_id):
    delete_book(book_id)
    return redirect(url_for('index'))


    


if __name__ == '__main__':
    init_db()

    print("Available routes:")
    print(app.url_map)

    app.run(debug=True, host='127.0.0.1', port=5000)




