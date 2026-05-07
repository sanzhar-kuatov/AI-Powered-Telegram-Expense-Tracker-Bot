import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def register_user(telegram_id, username, first_name):
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