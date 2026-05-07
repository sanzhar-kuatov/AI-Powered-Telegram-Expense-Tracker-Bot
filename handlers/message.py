from telegram import Update
from telegram.ext import ContextTypes

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Placeholder — AI classification will be wired in Phase 3
    await update.message.reply_text(
        f"📝 You said: *{text}*\n\n"
        "_(AI categorization coming soon!)_",
        parse_mode="Markdown"
    )