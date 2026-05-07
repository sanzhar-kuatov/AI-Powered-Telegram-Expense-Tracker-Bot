import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


# ─── Connection ───────────────────────────────────────────────

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# ─── Users ────────────────────────────────────────────────────

def register_user(telegram_id: int, username: str, first_name: str):
    """Save user to DB if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT IGNORE INTO users (telegram_id, username, first_name)
        VALUES (%s, %s, %s)
    """, (telegram_id, username, first_name))
    conn.commit()
    cursor.close()
    conn.close()


# ─── Categories ───────────────────────────────────────────────

def get_category_id(category_name: str) -> int | None:
    """Look up category ID by name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM categories WHERE name = %s", (category_name,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


# ─── Expenses ─────────────────────────────────────────────────

def save_expense(telegram_id: int, description: str, amount: float,
                 category_name: str, expense_date: str) -> bool:
    """Save a classified expense. Returns True on success."""
    category_id = get_category_id(category_name)
    if category_id is None:
        return False

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (user_id, description, amount, category_id, expense_date)
        VALUES (%s, %s, %s, %s, %s)
    """, (telegram_id, description, amount, category_id, expense_date))
    conn.commit()
    cursor.close()
    conn.close()
    return True


# ─── Conversations ────────────────────────────────────────────

def save_conversation(telegram_id: int, user_message: str, bot_reply: str):
    """Save a user message and the bot's reply."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (telegram_id, user_message, bot_reply)
        VALUES (%s, %s, %s)
    """, (telegram_id, user_message, bot_reply))
    conn.commit()
    cursor.close()
    conn.close()