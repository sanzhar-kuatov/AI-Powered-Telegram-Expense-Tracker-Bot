import time
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

CATEGORIES = [
    "Food", "Transport",
    "Home", "Health", "Entertainment", "Education",
    "Clothes", "Utilities", "Other"
]


# ─── Custom Exceptions ────────────────────────────────────────

class NoCreditsError(Exception):
    pass


# ─── Prompts ──────────────────────────────────────────────────

INTENT_PROMPT = """You are an intent classifier for an expense tracking bot.
Classify the user's message into exactly one intent.

Intents:
- EXPENSE: user is logging a new expense
- INCOME: user is logging income received
- EDIT: user wants to correct a previously logged expense
- OTHER: none of the above

Rules:
- Reply with ONE word only: EXPENSE, INCOME, EDIT, or OTHER
- No punctuation, no explanation

Examples:
"nasi lemak 5.50" → EXPENSE
"yesterday I got bananas 20rm" → EXPENSE
"received salary 15000rm" → INCOME
"today received gift 500rm" → INCOME
"wrong amount it was 15rm" → EDIT
"ID 32 price was 20rm" → EDIT
"its wrong category, its Home" → EDIT
"banana yesterday was 10rm not 5rm" → EDIT
"hello how are you" → OTHER"""

EXTRACTION_PROMPT = """You are an expense extraction assistant for a Malaysian user.
Extract the item name, amount, and date from a casual message.

Rules:
- Reply in this exact format: ITEM|AMOUNT|DATE
- ITEM: short description of what was bought (in English)
- AMOUNT: number only, no currency symbols. If not found, use 0.00
- DATE: in YYYY-MM-DD format.
  - If user says "yesterday", use YESTERDAY
  - If user gives a date like "01.05.2023", convert to YYYY-MM-DD
  - If no date mentioned, use TODAY
- Do not include any other text

Today's date context will be provided in each message.

Examples:
"nasi lemak 5.50" → nasi lemak|5.50|TODAY
"yesterday I got bananas 20rm" → bananas|20.00|YESTERDAY
"01.05.2023 apples - 10rm" → apples|10.00|2023-05-01
"spent 89 on nike shirt today" → nike shirt|89.00|TODAY"""

INCOME_PROMPT = """You are an income extraction assistant for a Malaysian user.
Extract the income description and amount from a casual message.

Rules:
- Reply in this exact format: DESCRIPTION|AMOUNT|DATE
- DESCRIPTION: short label for the income source (in English)
- AMOUNT: number only, no currency symbols. If not found, use 0.00
- DATE: in YYYY-MM-DD format. Use TODAY or YESTERDAY if applicable.
- Do not include any other text

Today's date context will be provided in each message.

Examples:
"today received salary 15000rm" → salary|15000.00|TODAY
"received gift 1000rm" → gift|1000.00|TODAY
"got bonus 2000 yesterday" → bonus|2000.00|YESTERDAY
"freelance payment 500rm 01.05.2025" → freelance payment|500.00|2025-05-01"""

EDIT_PROMPT = """You are an expense edit assistant.
Extract what the user wants to change about a previous expense.

Rules:
- Reply in this exact format: ID|FIELD|VALUE
- ID: the expense ID if mentioned, otherwise use LAST
- FIELD: one of — amount, category, description, date
- VALUE: the new value to set
  - For amount: number only
  - For category: must be one of: Food, Transport, Shopping, Home, Health, Entertainment, Other
  - For description: short item name
  - For date: YYYY-MM-DD format
- Do not include any other text

Today's date context will be provided in each message.

Examples:
"wrong amount it was 15rm" → LAST|amount|15.00
"ID 32 price was 20rm" → 32|amount|20.00
"its wrong category, its Home" → LAST|category|Home
"ID 5 wrong item its actually transport" → 5|category|Transport
"banana yesterday was 10rm not 5rm" → LAST|amount|10.00
"ID 12 change date to 01.05.2025" → 12|date|2025-05-01
"wrong name, its chicken rice" → LAST|description|chicken rice"""

CLASSIFICATION_PROMPT = f"""You are an expense categorization assistant.
Classify the given expense into exactly one category.

Available categories: {", ".join(CATEGORIES)}

Rules:
- Reply in this exact format: CATEGORY|CONFIDENCE
- CATEGORY must be one of the available categories listed above
- CONFIDENCE is your certainty from 0 to 100
- Do not include any other text

Examples:
nasi lemak → Food|98
grab to office → Transport|95
panadol → Health|97
new blender → Home|92
nike shoes → Shopping|90
netflix → Entertainment|88
random item → Other|60"""


# ─── Private Helpers ──────────────────────────────────────────

def _call_claude(system: str, user_message: str, max_tokens: int = 30) -> str:
    retries = 3
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text.strip()
        except anthropic.APIStatusError as e:
            error_message = str(e).lower()
            if "credit" in error_message or "billing" in error_message or e.status_code == 402:
                raise NoCreditsError("Anthropic account has no credits remaining.")
            if e.status_code in (429, 529) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise e


def _resolve_date(date_raw: str, today: str, yesterday: str) -> str:
    d = date_raw.strip().upper()
    if d == "TODAY":
        return today
    if d == "YESTERDAY":
        return yesterday
    return date_raw.strip()


def _parse_extraction(raw: str, today: str, yesterday: str) -> tuple[str, float, str]:
    parts = raw.split("|") if "|" in raw else []
    if len(parts) == 3:
        item = parts[0].strip()
        try:
            amount = float(parts[1].strip())
        except ValueError:
            amount = 0.00
        date = _resolve_date(parts[2], today, yesterday)
        return item, amount, date
    return raw.strip(), 0.00, today


def _parse_classification(raw: str) -> tuple[str, int]:
    if "|" in raw:
        parts = raw.split("|", 1)
        category = parts[0].strip()
        try:
            confidence = int(parts[1].strip())
        except ValueError:
            confidence = 50
        if category not in CATEGORIES:
            category = "Other"
            confidence = 50
        return category, confidence
    return "Other", 50


def _parse_edit(raw: str) -> tuple[str, str, str]:
    """Parse 'ID|FIELD|VALUE' edit response."""
    parts = raw.split("|") if "|" in raw else []
    if len(parts) == 3:
        return parts[0].strip(), parts[1].strip().lower(), parts[2].strip()
    return "LAST", "amount", "0"


def _parse_income(raw: str, today: str, yesterday: str) -> tuple[str, float, str]:
    parts = raw.split("|") if "|" in raw else []
    if len(parts) == 3:
        description = parts[0].strip()
        try:
            amount = float(parts[1].strip())
        except ValueError:
            amount = 0.00
        date = _resolve_date(parts[2], today, yesterday)
        return description, amount, date
    return raw.strip(), 0.00, today


# ─── Public Functions ─────────────────────────────────────────

def detect_intent(user_message: str) -> str:
    """Returns: EXPENSE | INCOME | EDIT | OTHER"""
    raw = _call_claude(INTENT_PROMPT, user_message, max_tokens=10)
    intent = raw.strip().upper()
    return intent if intent in ("EXPENSE", "INCOME", "EDIT", "OTHER") else "OTHER"


def extract_expense(user_message: str, today: str, yesterday: str) -> tuple[str, float, str]:
    prompt = f"Today is {today}. Yesterday was {yesterday}.\n\n{user_message}"
    raw = _call_claude(EXTRACTION_PROMPT, prompt)
    return _parse_extraction(raw, today, yesterday)


def extract_income(user_message: str, today: str, yesterday: str) -> tuple[str, float, str]:
    prompt = f"Today is {today}. Yesterday was {yesterday}.\n\n{user_message}"
    raw = _call_claude(INCOME_PROMPT, prompt)
    return _parse_income(raw, today, yesterday)


def extract_edit(user_message: str, today: str, yesterday: str) -> tuple[str, str, str]:
    """Returns (expense_id_or_LAST, field, new_value)."""
    prompt = f"Today is {today}. Yesterday was {yesterday}.\n\n{user_message}"
    raw = _call_claude(EDIT_PROMPT, prompt)
    return _parse_edit(raw)


def classify_expense(description: str) -> tuple[str, int]:
    raw = _call_claude(CLASSIFICATION_PROMPT, description)
    return _parse_classification(raw)
