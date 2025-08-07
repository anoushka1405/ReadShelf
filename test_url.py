import sqlite3

DB_NAME = 'books.db'  # update if needed

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("SELECT id, title, status FROM books")
books = c.fetchall()
conn.close()

for book in books:
    print(f"ID: {book[0]}, Title: {book[1]}, Status: {book[2]}")
