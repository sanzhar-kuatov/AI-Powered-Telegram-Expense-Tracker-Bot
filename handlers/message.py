from datetime import date
from telegram import Update
from telegram.ext import ContextTypes
from ai import extract_expense, classify_expense, NoCreditsError
from db import save_expense, save_conversation


# ─── Helpers ──────────────────────────────────────────────────

def _confidence_label(confidence: int) -> str:
    """Convert confidence score to a visual label."""
    if confidence >= 85:
        return f"🟢 High ({confidence}%)"
    elif confidence >= 60:
        return f"🟡 Medium ({confidence}%)"
    else:
        return f"🔴 Low ({confidence}%)"


def _build_reply(description: str, amount: float,
                 category: str, confidence: int) -> str:
    """Build the success reply message."""
    amount_display = f"RM {amount:.2f}" if amount > 0 else "_No amount detected_"
    return (
        f"✅ *Expense Saved!*\n\n"
        f"📝 Item: {description}\n"
        f"💰 Amount: {amount_display}\n"
        f"🏷️ Category: *{category}*\n"
        f"📊 Confidence: {_confidence_label(confidence)}"
    )


# ─── Handler ──────────────────────────────────────────────────

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text.strip()

    thinking_msg = await update.message.reply_text("🤔 Processing your expense...")

    try:
        # Step 1: Extract item + amount from free-form message
        description, amount = extract_expense(user_message)

        # Step 2: Classify the extracted item
        category, confidence = classify_expense(description)

        # Step 3: Save expense to DB
        today = date.today().strftime("%Y-%m-%d")
        save_expense(user.id, description, amount, category, today)

        # Step 4: Build and send reply
        bot_reply = _build_reply(description, amount, category, confidence)
        await thinking_msg.edit_text(bot_reply, parse_mode="Markdown")

    except NoCreditsError:
        bot_reply = (
            "❌ *No API Credits Available*\n\n"
            "The bot has run out of AI credits and cannot process expenses right now.\n"
            "Please top up at console.anthropic.com."
        )
        await thinking_msg.edit_text(bot_reply, parse_mode="Markdown")

    except Exception as e:
        bot_reply = "❌ Something went wrong. Please try again."
        await thinking_msg.edit_text(bot_reply)
        print(f"Error in message_handler: {e}")

    finally:
        # Always save the conversation regardless of outcome
        save_conversation(user.id, user_message, bot_reply)