import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# These must match exactly what's in your categories table
CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Home",
    "Health",
    "Entertainment",
    "Other"
]

SYSTEM_PROMPT = f"""You are an expense categorization assistant. 
Your job is to classify expense descriptions into exactly one category.

Available categories: {", ".join(CATEGORIES)}

Rules:
- Reply in this exact format: CATEGORY|CONFIDENCE
- CATEGORY must be one of the available categories above
- CONFIDENCE must be a number from 0 to 100 (your certainty %)
- Do not include any other text, explanation, or punctuation
- If unsure, pick the closest match and use a lower confidence score

Examples:
nasi lemak → Food|98
grab to office → Transport|95
panadol → Health|97
new blender → Home|92
nike shoes → Shopping|90
netflix subscription → Entertainment|88
some random thing → Other|60"""


def classify_expense(description: str) -> tuple[str, int]:
    """
    Send expense description to Claude and return (category, confidence).
    """
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=20,  # We only need a short reply e.g. "Food|98"
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": description}
        ]
    )

    raw = response.content[0].text.strip()

    # Parse the "CATEGORY|CONFIDENCE" response
    if "|" in raw:
        parts = raw.split("|")
        category = parts[0].strip()
        confidence = int(parts[1].strip())

        # Validate category is one we recognise
        if category not in CATEGORIES:
            category = "Other"
            confidence = 50
    else:
        # Fallback if Claude returns unexpected format
        category = "Other"
        confidence = 50

    return category, confidence