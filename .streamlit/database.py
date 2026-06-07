import sqlite3

DB_NAME = "chat.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,
        content TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tips(
        chat_id INTEGER PRIMARY KEY,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_chat(title="New Chat"):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO chats(title) VALUES(?)",
        (title,)
    )

    chat_id = cur.lastrowid

    conn.commit()
    conn.close()

    return chat_id


def get_chats():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT id,title FROM chats ORDER BY id DESC"
    )

    rows = cur.fetchall()

    conn.close()

    return rows


def update_chat_title(chat_id, title):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "UPDATE chats SET title=? WHERE id=?",
        (title, chat_id)
    )

    conn.commit()
    conn.close()


def delete_chat(chat_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM messages WHERE chat_id=?",
        (chat_id,)
    )

    cur.execute(
        "DELETE FROM tips WHERE chat_id=?",
        (chat_id,)
    )

    cur.execute(
        "DELETE FROM chats WHERE id=?",
        (chat_id,)
    )

    conn.commit()
    conn.close()


def add_message(chat_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO messages
        (chat_id, role, content)
        VALUES (?, ?, ?)
        """,
        (chat_id, role, content)
    )

    conn.commit()
    conn.close()


def get_messages(chat_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, content
        FROM messages
        WHERE chat_id=?
        ORDER BY id
        """,
        (chat_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows


def save_tips(chat_id, content):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO tips
        (chat_id, content)
        VALUES (?, ?)
        """,
        (chat_id, content)
    )

    conn.commit()
    conn.close()


def get_tips(chat_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT content
        FROM tips
        WHERE chat_id=?
        """,
        (chat_id,)
    )

    row = cur.fetchone()

    conn.close()

    return row[0] if row else ""