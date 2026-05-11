from telegram import Update
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Expense Tracker Bot — Help*\n\n"

        "━━━━━━━━━━━━━━━━\n"
        "💸 *Log an Expense*\n"
        "Just describe your expense naturally:\n"
        "`nasi lemak 5.50`\n"
        "`spent 89 on nike shirt today`\n"
        "`yesterday I got bananas 20rm`\n"
        "`01.05.2025 apples - 10rm`\n\n"

        "━━━━━━━━━━━━━━━━\n"
        "💵 *Log Income*\n"
        "Mention receiving money:\n"
        "`received salary 15000rm`\n"
        "`today received gift 500rm`\n"
        "`got bonus 2000 yesterday`\n\n"

        "━━━━━━━━━━━━━━━━\n"
        "✏️ *Edit an Expense*\n"
        "Each saved expense shows an 🆔 ID. Use it to edit precisely:\n"
        "`ID 32 price was 20rm`\n"
        "`ID 5 wrong category, its Transport`\n"
        "Or refer to your last expense without an ID:\n"
        "`wrong amount, it's 15rm`\n"
        "`its wrong category, its Home`\n\n"

        "━━━━━━━━━━━━━━━━\n"
        "📊 *Generate a Report*\n"
        "Include the word *report* with a date range:\n"
        "`give me report for 01.01.2025-30.04.2025`\n"
        "The bot will send an Excel file with your income, "
        "expenses, and net balance.\n\n"

        "━━━━━━━━━━━━━━━━\n"
        "⚠️ *Important Notes*\n"
        "• Send *one item per message* — the AI processes "
        "one request at a time\n"
        "• ❌ Don't do this: _'bananas 5rm and apples 10rm'_\n"
        "• ✅ Do this: send each item as a separate message\n"
        "• Do not mix a log request with a report request "
        "in the same message",
        parse_mode="Markdown"
    )