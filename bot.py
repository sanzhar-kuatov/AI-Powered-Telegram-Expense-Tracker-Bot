from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN
from handlers.start import start_handler
from handlers.help import help_handler
from handlers.message import message_handler

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))

    # Register message handler (catches all plain text messages)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()