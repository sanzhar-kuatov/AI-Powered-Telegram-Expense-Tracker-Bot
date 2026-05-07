from telegram import Update
from telegram.ext import ContextTypes
from ai import classify_expense

def parse_expense(text: str):
    """
    Try to split user input into (description, amount).
    Expects format like: 'nasi lemak 5.50' or 'grab 12'
    Returns (description, amount) or (None, None) if invalid.
    """
    parts = text.rsplit(" ", 1)  # split from the right, once
    if len(parts) == 2:
        try:
            amount = float(parts[1])
            description = parts[0].strip()
            return description, amount
        except ValueError:
            pass
    return None, None


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    description, amount = parse_expense(text)

    if description is None:
        await update.message.reply_text(
            "⚠️ I couldn't understand that.\n\n"
            "Please use this format:\n"
            "`<item> <amount>`\n\n"
            "Example: `nasi lemak 5.50`",
            parse_mode="Markdown"
        )
        return

    # Show a "thinking" message while AI processes
    thinking_msg = await update.message.reply_text("🤔 Categorizing your expense...")

    try:
        category, confidence = classify_expense(description)

        # Build confidence indicator
        if confidence >= 85:
            confidence_label = "🟢 High"
        elif confidence >= 60:
            confidence_label = "🟡 Medium"
        else:
            confidence_label = "🔴 Low"

        await thinking_msg.edit_text(
            f"✅ *Expense Logged!*\n\n"
            f"📝 Item: {description}\n"
            f"💰 Amount: RM {amount:.2f}\n"
            f"🏷️ Category: *{category}*\n"
            f"📊 Confidence: {confidence_label} ({confidence}%)\n\n"
            f"_(Database saving coming next!)_",
            parse_mode="Markdown"
        )

    except Exception as e:
        await thinking_msg.edit_text(
            "❌ Sorry, I couldn't classify that expense. Please try again."
        )
        print(f"AI error: {e}")