import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

CATEGORIES = [
    "Food", "Transport", "Clothes",
    "Home", "Health", "Entertainment", "Education", "Utilities", "Other"
]


# ─── Custom Exceptions ────────────────────────────────────────

class NoCreditsError(Exception):
    pass


# ─── Prompts ──────────────────────────────────────────────────

EXTRACTION_PROMPT = """You are an expense extraction assistant for a Malaysian user.
Extract the item name, amount, and date from a casual message.

Rules:
- Reply in this exact format: ITEM|AMOUNT|DATE
- ITEM: short description of what was bought (in English)
- AMOUNT: number only, no currency symbols. If not found, use 0.00
- DATE: in YYYY-MM-DD format.
  - If user says "yesterday", calculate yesterday's date
  - If user gives a date like "01.05.2023" or "1/5/2023", convert to YYYY-MM-DD
  - If no date mentioned, use TODAY
- Do not include any other text

Today's date context will be provided in each message.

Examples:
"nasi lemak 5.50" → nasi lemak|5.50|TODAY
"yesterday I got bananas 20rm" → bananas|20.00|YESTERDAY
"01.05.2023 apples - 10rm" → apples|10.00|2023-05-01
"grab to office rm12 last monday" → grab to office|12.00|LAST_MONDAY
"spent 89 on nike shirt today" → nike shirt|89.00|TODAY
"panadol at guardian rm8.90" → panadol|8.90|TODAY"""

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
        raise e


def _parse_extraction(raw: str, today: str, yesterday: str) -> tuple[str, float, str]:
    """Parse 'ITEM|AMOUNT|DATE' response from Claude."""
    parts = raw.split("|") if "|" in raw else []
    if len(parts) == 3:
        item = parts[0].strip()
        try:
            amount = float(parts[1].strip())
        except ValueError:
            amount = 0.00
        date_raw = parts[2].strip().upper()
        if date_raw == "TODAY":
            date = today
        elif date_raw == "YESTERDAY":
            date = yesterday
        else:
            date = parts[2].strip()  # Already in YYYY-MM-DD from Claude
        return item, amount, date
    return raw.strip(), 0.00, today


def _parse_classification(raw: str) -> tuple[str, int]:
    """Parse 'CATEGORY|CONFIDENCE' response from Claude."""
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


# ─── Public Functions ─────────────────────────────────────────

def extract_expense(user_message: str, today: str, yesterday: str) -> tuple[str, float, str]:
    """
    Extract item, amount, and date from a free-form message.
    Returns (item, amount, date).
    """
    prompt_with_date = f"Today is {today}. Yesterday was {yesterday}.\n\n{user_message}"
    raw = _call_claude(EXTRACTION_PROMPT, prompt_with_date)
    return _parse_extraction(raw, today, yesterday)


def classify_expense(description: str) -> tuple[str, int]:
    """
    Classify an expense description into a category.
    Returns (category, confidence).
    """
    raw = _call_claude(CLASSIFICATION_PROMPT, description)
    return _parse_classification(raw)