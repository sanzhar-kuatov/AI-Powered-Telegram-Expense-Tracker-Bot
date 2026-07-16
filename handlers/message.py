import re
from datetime import date, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from ai import (detect_intent, extract_expense, extract_income,
                extract_edit, classify_expense, NoCreditsError)
from db import (save_expense, save_income, get_last_expense_id,
                edit_expense, get_expense_by_id, save_conversation)
from report import generate_report


# ─── Date Helpers ─────────────────────────────────────────────

def _today_yesterday() -> tuple[str, str]:
    today     = date.today().strftime("%Y-%m-%d")
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    return today, yesterday

def _parse_report_dates(text: str) -> tuple[str, str] | tuple[None, None]:
    pattern = r'(\d{1,2})[./](\d{1,2})[./](\d{4})\s*[-–]\s*(\d{1,2})[./](\d{1,2})[./](\d{4})'
    match = re.search(pattern, text)
    if match:
        d1, m1, y1, d2, m2, y2 = match.groups()
        return f"{y1}-{m1.zfill(2)}-{d1.zfill(2)}", f"{y2}-{m2.zfill(2)}-{d2.zfill(2)}"
    return None, None

def _is_report_request(text: str) -> bool:
    return any(kw in text.lower() for kw in ["report", "summary", "give me", "show me"])


# ─── Reply Builders ───────────────────────────────────────────

def _confidence_label(confidence: int) -> str:
    if confidence >= 85:   return f"🟢 High ({confidence}%)"
    elif confidence >= 60: return f"🟡 Medium ({confidence}%)"
    else:                  return f"🔴 Low ({confidence}%)"

def _expense_reply(expense_id: int, description: str, amount: float,
                   category: str, confidence: int, expense_date: str) -> str:
    amount_str = f"RM {amount:.2f}" if amount > 0 else "_No amount detected_"
    return (
        f"✅ *Expense Saved!*\n\n"
        f"🆔 ID: `{expense_id}`\n"
        f"📅 Date: {expense_date}\n"
        f"📝 Item: {description}\n"
        f"💰 Amount: {amount_str}\n"
        f"🏷️ Category: *{category}*\n"
        f"📊 Confidence: {_confidence_label(confidence)}\n\n"
        f"_To edit this expense, mention its ID or say 'wrong ...'_"
    )

def _income_reply(income_id: int, description: str,
                  amount: float, income_date: str) -> str:
    return (
        f"💵 *Income Saved!*\n\n"
        f"🆔 ID: `{income_id}`\n"
        f"📅 Date: {income_date}\n"
        f"📝 Source: {description}\n"
        f"💰 Amount: RM {amount:.2f}"
    )

def _edit_reply(expense: dict, field: str, new_value: str) -> str:
    return (
        f"✏️ *Expense Updated!*\n\n"
        f"🆔 ID: `{expense['id']}`\n"
        f"📝 Item: {expense['description']}\n"
        f"💰 Amount: RM {float(expense['amount']):.2f}\n"
        f"🏷️ Category: {expense['category']}\n"
        f"📅 Date: {expense['expense_date']}\n\n"
        f"✅ Changed *{field}* → `{new_value}`"
    )


# ─── Sub-Handlers ─────────────────────────────────────────────

async def _handle_report(update: Update, telegram_id: int,
                          user_message: str, date_from: str, date_to: str):
    thinking = await update.message.reply_text("📊 Generating your report...")
    bot_reply = ""
    try:
        buffer   = generate_report(telegram_id, date_from, date_to)
        filename = f"report_{date_from}_to_{date_to}.xlsx"
        bot_reply = f"Report generated: {date_from} to {date_to}."
        await update.message.reply_document(
            document=buffer, filename=filename,
            caption=f"📊 Financial report from *{date_from}* to *{date_to}*",
            parse_mode="Markdown"
        )
        await thinking.delete()
    except Exception as e:
        bot_reply = "❌ Could not generate report. Please try again."
        await thinking.edit_text(bot_reply)
        print(f"Report error: {e}")
    finally:
        save_conversation(telegram_id, user_message, bot_reply)


async def _handle_expense(update: Update, telegram_id: int, user_message: str):
    thinking  = await update.message.reply_text("🤔 Processing your expense...")
    bot_reply = ""
    try:
        today, yesterday = _today_yesterday()
        description, amount, expense_date = extract_expense(user_message, today, yesterday)
        category, confidence = classify_expense(description)
        expense_id = save_expense(telegram_id, description, amount, category, expense_date)
        bot_reply  = _expense_reply(expense_id, description, amount,
                                    category, confidence, expense_date)
        await thinking.edit_text(bot_reply, parse_mode="Markdown")
    except NoCreditsError:
        bot_reply = "❌ *No API Credits Available*\n\nPlease top up at console.anthropic.com."
        await thinking.edit_text(bot_reply, parse_mode="Markdown")
    except Exception as e:
        bot_reply = "❌ Something went wrong. Please try again."
        await thinking.edit_text(bot_reply)
        print(f"Expense error: {e}")
    finally:
        save_conversation(telegram_id, user_message, bot_reply)


async def _handle_income(update: Update, telegram_id: int, user_message: str):
    thinking  = await update.message.reply_text("💵 Processing your income...")
    bot_reply = ""
    try:
        today, yesterday = _today_yesterday()
        description, amount, income_date = extract_income(user_message, today, yesterday)
        income_id = save_income(telegram_id, description, amount, income_date)
        bot_reply = _income_reply(income_id, description, amount, income_date)
        await thinking.edit_text(bot_reply, parse_mode="Markdown")
    except NoCreditsError:
        bot_reply = "❌ *No API Credits Available*\n\nPlease top up at console.anthropic.com."
        await thinking.edit_text(bot_reply, parse_mode="Markdown")
    except Exception as e:
        bot_reply = "❌ Something went wrong. Please try again."
        await thinking.edit_text(bot_reply)
        print(f"Income error: {e}")
    finally:
        save_conversation(telegram_id, user_message, bot_reply)


async def _handle_edit(update: Update, telegram_id: int, user_message: str):
    thinking  = await update.message.reply_text("✏️ Processing your edit...")
    bot_reply = ""
    try:
        today, yesterday = _today_yesterday()
        expense_id_raw, field, new_value = extract_edit(user_message, today, yesterday)

        # Resolve LAST to actual ID
        if expense_id_raw.upper() == "LAST":
            expense_id = get_last_expense_id(telegram_id)
            if expense_id is None:
                bot_reply = "⚠️ No previous expense found to edit."
                await thinking.edit_text(bot_reply)
                return
        else:
            try:
                expense_id = int(expense_id_raw)
            except ValueError:
                expense_id = get_last_expense_id(telegram_id)

        success = edit_expense(expense_id, telegram_id, field, new_value)
        if success:
            updated = get_expense_by_id(expense_id, telegram_id)
            bot_reply = _edit_reply(updated, field, new_value)
            await thinking.edit_text(bot_reply, parse_mode="Markdown")
        else:
            bot_reply = (f"⚠️ Could not update expense `ID {expense_id}`.\n"
                         "Please check the ID and try again.")
            await thinking.edit_text(bot_reply, parse_mode="Markdown")

    except NoCreditsError:
        bot_reply = "❌ *No API Credits Available*\n\nPlease top up at console.anthropic.com."
        await thinking.edit_text(bot_reply, parse_mode="Markdown")
    except Exception as e:
        bot_reply = "❌ Something went wrong. Please try again."
        await thinking.edit_text(bot_reply)
        print(f"Edit error: {e}")
    finally:
        save_conversation(telegram_id, user_message, bot_reply)


# ─── Main Handler ─────────────────────────────────────────────

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user         = update.effective_user
    user_message = update.message.text.strip()

    # Report check first (no AI needed)
    if _is_report_request(user_message):
        date_from, date_to = _parse_report_dates(user_message)
        if date_from and date_to:
            await _handle_report(update, user.id, user_message, date_from, date_to)
        else:
            await update.message.reply_text(
                "📅 Please include a date range.\n\n"
                "Example: `give me report for 01.01.2025-30.04.2025`",
                parse_mode="Markdown"
            )
        return

    # Use AI to detect intent
    try:
        intent = detect_intent(user_message)
    except NoCreditsError:
        await update.message.reply_text(
            "❌ *No API Credits Available*\n\nPlease top up at console.anthropic.com.",
            parse_mode="Markdown"
        )
        return
    except Exception as e:
        await update.message.reply_text("❌ Something went wrong. Please try again.")
        print(f"Intent detection error: {e}")
        return

    if intent == "INCOME":
        await _handle_income(update, user.id, user_message)
    elif intent == "EDIT":
        await _handle_edit(update, user.id, user_message)
    elif intent == "EXPENSE":
        await _handle_expense(update, user.id, user_message)
    else:
        await update.message.reply_text(
            "🤔 I didn't quite understand that.\n\n"
            "Try logging an expense like `nasi lemak 5.50`, "
            "or type /help to see what I can do.",
            parse_mode="Markdown"
        )
