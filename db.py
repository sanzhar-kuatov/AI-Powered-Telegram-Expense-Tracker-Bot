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
                 category_name: str, expense_date: str) -> int:
    """Save expense and return its new ID."""
    category_id = get_category_id(category_name)
    if category_id is None:
        return -1
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (user_id, description, amount, category_id, expense_date)
        VALUES (%s, %s, %s, %s, %s)
    """, (telegram_id, description, amount, category_id, expense_date))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id


def get_last_expense_id(telegram_id: int) -> int | None:
    """Get the most recently saved expense ID for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM expenses
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (telegram_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def edit_expense(expense_id: int, telegram_id: int,
                 field: str, value: str) -> bool:
    """
    Edit a specific field of an expense.
    Returns True if a row was actually updated.
    """
    allowed_fields = {"amount", "description", "expense_date"}
    conn = get_connection()
    cursor = conn.cursor()

    if field == "category":
        category_id = get_category_id(value)
        if category_id is None:
            return False
        cursor.execute("""
            UPDATE expenses SET category_id = %s
            WHERE id = %s AND user_id = %s
        """, (category_id, expense_id, telegram_id))
    elif field in allowed_fields:
        db_field = "expense_date" if field == "date" else field
        cursor.execute(f"""
            UPDATE expenses SET {db_field} = %s
            WHERE id = %s AND user_id = %s
        """, (value, expense_id, telegram_id))
    else:
        return False

    updated = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return updated


def get_expense_by_id(expense_id: int, telegram_id: int) -> dict | None:
    """Fetch a single expense row as a dict."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.id, e.description, e.amount, c.name as category, e.expense_date
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.id = %s AND e.user_id = %s
    """, (expense_id, telegram_id))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_expenses_by_period(telegram_id: int, date_from: str, date_to: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.description, e.amount, c.name, e.expense_date
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s AND e.expense_date BETWEEN %s AND %s
        ORDER BY e.expense_date ASC
    """, (telegram_id, date_from, date_to))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_category_summary(telegram_id: int, date_from: str, date_to: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s AND e.expense_date BETWEEN %s AND %s
        GROUP BY c.name
        ORDER BY total DESC
    """, (telegram_id, date_from, date_to))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# ─── Income ───────────────────────────────────────────────────

def save_income(telegram_id: int, description: str,
                amount: float, income_date: str) -> int:
    """Save income and return its new ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO income (user_id, description, amount, income_date)
        VALUES (%s, %s, %s, %s)
    """, (telegram_id, description, amount, income_date))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id


def get_income_by_period(telegram_id: int, date_from: str, date_to: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT description, amount, income_date
        FROM income
        WHERE user_id = %s AND income_date BETWEEN %s AND %s
        ORDER BY income_date ASC
    """, (telegram_id, date_from, date_to))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_income_summary(telegram_id: int, date_from: str, date_to: str) -> float:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM income
        WHERE user_id = %s AND income_date BETWEEN %s AND %s
    """, (telegram_id, date_from, date_to))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return float(row[0]) if row else 0.0


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