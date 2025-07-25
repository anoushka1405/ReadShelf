import sqlite3

DB_NAME = 'books.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            mood TEXT,
            review TEXT,
            rating INTEGER,
            status TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS blurbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()



def add_book(title, author, mood, review, rating, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO books (title, author, mood, review, rating, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, author, mood, review, rating, status))
    conn.commit()
    conn.close()

def save_blurb(content):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute('INSERT INTO blurbs (content) VALUES (?)', (content,))
    conn.commit()
    conn.close()

def get_latest_blurb():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute('SELECT content FROM blurbs ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def get_all_books(status='read'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE status=?", (status,))
    books = c.fetchall()
    conn.close()
    return books

def delete_book(book_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()


