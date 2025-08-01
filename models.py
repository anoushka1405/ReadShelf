import sqlite3

DB_NAME = 'books.db'

# 🧱 Database Initialization
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create books table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            mood TEXT,
            review TEXT,
            rating INTEGER,
            status TEXT,
            page_count INTEGER,
            description TEXT,
            thumbnail TEXT,
            categories TEXT
        )
    ''')

    # Create blurbs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS blurbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT
        )
    ''')

    conn.commit()
    conn.close()

# 📚 Book Management
def add_book(title, author, mood, review, rating, status,
             page_count=None, description=None, thumbnail=None, categories=None):
    """Add a new book to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO books (
            title, author, mood, review, rating, status,
            page_count, description, thumbnail, categories
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, mood, review, rating, status,
          page_count, description, thumbnail, categories))
    conn.commit()
    conn.close()

def get_all_books(status='read'):
    """Retrieve all books with a given status."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE status=?", (status,))
    books = c.fetchall()
    conn.close()
    return books

def delete_book(book_id):
    """Delete a book by its ID."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

# ✨ Blurb Management
def save_blurb(content):
    """Save a generated blurb to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO blurbs (content) VALUES (?)', (content,))
    conn.commit()
    conn.close()

def get_latest_blurb():
    """Retrieve the most recent blurb."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT content FROM blurbs ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
