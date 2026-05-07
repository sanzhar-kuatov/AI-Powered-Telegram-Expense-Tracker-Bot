import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

CATEGORIES = [
    "Food", "Transport", "Shopping",
    "Home", "Health", "Entertainment", "Other"
]

# ─── Custom Exceptions ────────────────────────────────────────

class NoCreditsError(Exception):
    """Raised when Anthropic account has no credits left."""
    pass


# ─── Prompts ──────────────────────────────────────────────────

EXTRACTION_PROMPT = """You are an expense extraction assistant for a Malaysian user.
Your job is to extract the item name and amount from a casual message.

Rules:
- Reply in this exact format: ITEM|AMOUNT
- ITEM is a short description of what was bought (in English)
- AMOUNT is a number only (no currency symbols)
- If no amount is found, use AMOUNT as 0.00
- Do not include any other text

Examples:
"just bought nasi lemak for 5.50" → nasi lemak|5.50
"rm12 grab to office" → grab to office|12.00
"spent 89 on nike shirt today" → nike shirt|89.00
"panadol at guardian, rm8.90" → panadol|8.90
"netflix 17" → netflix|17.00
"blender" → blender|0.00"""

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
    """Make a Claude API call. Raises NoCreditsError if out of credits."""
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text.strip()

    except anthropic.BadRequestError as e:
        raise e

    except anthropic.APIStatusError as e:
        # Catch billing/credit errors
        error_message = str(e).lower()
        if "credit" in error_message or "billing" in error_message or e.status_code == 402:
            raise NoCreditsError("Anthropic account has no credits remaining.")
        raise e


def _parse_extraction(raw: str) -> tuple[str, float]:
    """Parse 'ITEM|AMOUNT' response from Claude."""
    if "|" in raw:
        parts = raw.split("|", 1)
        item = parts[0].strip()
        try:
            amount = float(parts[1].strip())
        except ValueError:
            amount = 0.00
        return item, amount
    return raw.strip(), 0.00


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

def extract_expense(user_message: str) -> tuple[str, float]:
    """
    Extract item name and amount from a free-form message.
    Returns (item, amount).
    """
    raw = _call_claude(EXTRACTION_PROMPT, user_message)
    return _parse_extraction(raw)


def classify_expense(description: str) -> tuple[str, int]:
    """
    Classify an expense description into a category.
    Returns (category, confidence).
    """
    raw = _call_claude(CLASSIFICATION_PROMPT, description)
    return _parse_classification(raw)