from telegram import Update
from telegram.ext import ContextTypes
from db import register_user

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Save user to database
    register_user(user.id, user.username, user.first_name)

    await update.message.reply_text(
        f"👋 Hello, {user.first_name}! Welcome to your Expense Tracker Bot.\n\n"
        "I can help you log and categorize your daily expenses.\n\n"
        "Type /help to see what I can do!"
    )