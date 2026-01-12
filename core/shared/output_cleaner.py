import re
import textwrap

_META_PREFIXES = [
    r"^Here is the .*?:\s*",
    r"^Sure, here is .*?:\s*",
    r"^I can help with that[\.:]\s*",
    r"^Okay, .*?[\.:]\s*",
    r"^Below is .*?[\.:]\s*",
    r"^Certainly! .*?[\.:]\s*",
]

# Extra-safe trims for “thinking” style openers (keep conservative)
_THINKING_OPENERS = [
    r"^I just received (a|the) (query|prompt|request)[\s\S]{0,200}?\.\s*",
    r"^It seems straightforward[\s\S]{0,200}?\.\s*",
]

def clean_output(text: str, max_line_length: int = 80) -> str:
    """
    Normalizes output text by:
    1) Normalizing whitespace (preserving paragraphs)
    2) Stripping common meta-commentary
    3) Limiting line length for prose only
    """
    if not text:
        return ""

    text = text.strip()

    # Strip common meta-commentary (start only)
    for pat in _META_PREFIXES:
        text = re.sub(pat, "", text, flags=re.IGNORECASE).lstrip()

    # If the model dumped “thinking” prose, trim a short generic opener
    # (only at start, only once)
    for pat in _THINKING_OPENERS:
        new_text = re.sub(pat, "", text, flags=re.IGNORECASE).lstrip()
        if new_text != text:
            text = new_text
            break

    if not text:
        return ""

    # Split paragraphs
    paragraphs = re.split(r"\n\s*\n", text)
    cleaned = []

    wrapper = textwrap.TextWrapper(
        width=max_line_length,
        break_long_words=False,
        replace_whitespace=False,
    )

    for p in paragraphs:
        p = p.rstrip()
        if not p.strip():
            continue

        # Heuristic: preserve “structured” blocks (headings / bullets / code-ish)
        looks_structured = bool(
            re.match(r"^\s*(#{1,6}\s|[-*]\s|\d+\.\s|```|[A-Z][A-Z_ ]{2,}:\s*$)", p)
        )
        if looks_structured:
            cleaned.append(p.strip())
            continue

        # Otherwise reflow prose
        p_normalized = " ".join(p.split())
        cleaned.append(wrapper.fill(p_normalized))

    return "\n\n".join(cleaned).strip()
