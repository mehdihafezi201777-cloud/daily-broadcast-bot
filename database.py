import sqlite3

DB = "bot.db"


def connect():
    return sqlite3.connect(DB)


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO users(id) VALUES(?)",
        (user_id,)
    )

    conn.commit()
    conn.close()


def get_users():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users")
    users = [x[0] for x in cur.fetchall()]

    conn.close()

    return users


def save_setting(key, value):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO settings(key,value)
    VALUES(?,?)
    ON CONFLICT(key)
    DO UPDATE SET value=excluded.value
    """,
    (key,value))

    conn.commit()
    conn.close()


def get_setting(key):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT value FROM settings WHERE key=?",
        (key,)
    )

    result = cur.fetchone()

    conn.close()

    return result[0] if result else None
