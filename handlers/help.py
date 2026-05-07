from telegram import Update
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Expense Tracker Bot — Help*\n\n"
        "Here's what you can do:\n\n"
        "📌 *Commands:*\n"
        "/start — Start the bot\n"
        "/help — Show this help message\n\n"
        "💸 *Log an expense:*\n"
        "Just send a message in this format:\n"
        "`nasi lemak 5.50`\n"
        "`blender 120`\n\n"
        "I'll automatically categorize it for you!",
        parse_mode="Markdown"
    )