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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


# ─── Expenses ─────────────────────────────────────────────────

def save_expense(telegram_id: int, description: str, amount: float,
                 category_name: str, expense_date: str) -> bool:
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


def get_expenses_by_period(telegram_id: int, date_from: str, date_to: str) -> list:
    """Fetch all expenses for a user in a date range, sorted by date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.description, e.amount, c.name, e.expense_date
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s
          AND e.expense_date BETWEEN %s AND %s
        ORDER BY e.expense_date ASC
    """, (telegram_id, date_from, date_to))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_category_summary(telegram_id: int, date_from: str, date_to: str) -> list:
    """Fetch total spent per category for a user in a date range."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s
          AND e.expense_date BETWEEN %s AND %s
        GROUP BY c.name
        ORDER BY total DESC
    """, (telegram_id, date_from, date_to))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# ─── Conversations ────────────────────────────────────────────

def save_conversation(telegram_id: int, user_message: str, bot_reply: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (telegram_id, user_message, bot_reply)
        VALUES (%s, %s, %s)
    """, (telegram_id, user_message, bot_reply))
    conn.commit()
    cursor.close()
    conn.close()