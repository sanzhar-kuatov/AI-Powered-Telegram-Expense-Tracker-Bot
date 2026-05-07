import re
from datetime import date, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from ai import extract_expense, classify_expense, NoCreditsError
from db import save_expense, save_conversation
from report import generate_report


# ─── Date Helpers (Pure Python, no AI) ───────────────────────

def _parse_report_dates(text: str) -> tuple[str, str] | tuple[None, None]:
    """
    Detect report request and extract date range.
    Supports: DD.MM.YYYY-DD.MM.YYYY or DD/MM/YYYY-DD/MM/YYYY
    """
    pattern = r'(\d{1,2})[./](\d{1,2})[./](\d{4})\s*[-–]\s*(\d{1,2})[./](\d{1,2})[./](\d{4})'
    match = re.search(pattern, text)
    if match:
        d1, m1, y1, d2, m2, y2 = match.groups()
        date_from = f"{y1}-{m1.zfill(2)}-{d1.zfill(2)}"
        date_to   = f"{y2}-{m2.zfill(2)}-{d2.zfill(2)}"
        return date_from, date_to
    return None, None

def _is_report_request(text: str) -> bool:
    """Check if user is asking for a report."""
    keywords = ["report", "summary", "show me", "give me", "spending"]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


# ─── Reply Helpers ────────────────────────────────────────────

def _confidence_label(confidence: int) -> str:
    if confidence >= 85:
        return f"🟢 High ({confidence}%)"
    elif confidence >= 60:
        return f"🟡 Medium ({confidence}%)"
    else:
        return f"🔴 Low ({confidence}%)"

def _build_expense_reply(description: str, amount: float,
                          category: str, confidence: int,
                          expense_date: str) -> str:
    amount_display = f"RM {amount:.2f}" if amount > 0 else "_No amount detected_"
    return (
        f"✅ *Expense Saved!*\n\n"
        f"📅 Date: {expense_date}\n"
        f"📝 Item: {description}\n"
        f"💰 Amount: {amount_display}\n"
        f"🏷️ Category: *{category}*\n"
        f"📊 Confidence: {_confidence_label(confidence)}"
    )


# ─── Handlers ─────────────────────────────────────────────────

async def _handle_report(update: Update, telegram_id: int,
                          user_message: str, date_from: str, date_to: str):
    """Generate and send the Excel report."""
    thinking_msg = await update.message.reply_text("📊 Generating your report...")
    try:
        buffer = generate_report(telegram_id, date_from, date_to)
        filename = f"expense_report_{date_from}_to_{date_to}.xlsx"
        bot_reply = f"Report generated for {date_from} to {date_to}."
        await update.message.reply_document(
            document=buffer,
            filename=filename,
            caption=f"📊 Your expense report from *{date_from}* to *{date_to}*",
            parse_mode="Markdown"
        )
        await thinking_msg.delete()
    except Exception as e:
        bot_reply = "❌ Could not generate report. Please try again."
        await thinking_msg.edit_text(bot_reply)
        print(f"Report error: {e}")
    finally:
        save_conversation(telegram_id, user_message, bot_reply)


async def _handle_expense(update: Update, telegram_id: int, user_message: str):
    """Classify and save an expense."""
    thinking_msg = await update.message.reply_text("🤔 Processing your expense...")
    bot_reply = ""
    try:
        today     = date.today().strftime("%Y-%m-%d")
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        description, amount, expense_date = extract_expense(user_message, today, yesterday)
        category, confidence = classify_expense(description)
        save_expense(telegram_id, description, amount, category, expense_date)

        bot_reply = _build_expense_reply(description, amount, category,
                                          confidence, expense_date)
        await thinking_msg.edit_text(bot_reply, parse_mode="Markdown")

    except NoCreditsError:
        bot_reply = (
            "❌ *No API Credits Available*\n\n"
            "The bot has run out of AI credits.\n"
            "Please top up at console.anthropic.com."
        )
        await thinking_msg.edit_text(bot_reply, parse_mode="Markdown")

    except Exception as e:
        bot_reply = "❌ Something went wrong. Please try again."
        await thinking_msg.edit_text(bot_reply)
        print(f"Expense error: {e}")

    finally:
        save_conversation(telegram_id, user_message, bot_reply)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text.strip()

    # Check if user wants a report
    if _is_report_request(user_message):
        date_from, date_to = _parse_report_dates(user_message)
        if date_from and date_to:
            await _handle_report(update, user.id, user_message, date_from, date_to)
        else:
            await update.message.reply_text(
                "📅 Please include a date range in your report request.\n\n"
                "Example:\n"
                "`give me report for 01.01.2025-30.04.2025`",
                parse_mode="Markdown"
            )
        return

    # Otherwise treat as an expense
    await _handle_expense(update, user.id, user_message)