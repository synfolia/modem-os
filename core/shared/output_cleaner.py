import re
import textwrap

# Precompile all regex patterns for performance
_META_PREFIXES = [
    re.compile(r"^Here is the .*?:\s*", re.IGNORECASE),
    re.compile(r"^Sure, here is .*?:\s*", re.IGNORECASE),
    re.compile(r"^I can help with that[\.:]\s*", re.IGNORECASE),
    re.compile(r"^Okay, .*?[\.:]\s*", re.IGNORECASE),
    re.compile(r"^Below is .*?[\.:]\s*", re.IGNORECASE),
    re.compile(r"^Certainly! .*?[\.:]\s*", re.IGNORECASE),
]

# Extra-safe trims for "thinking" style openers (keep conservative)
_THINKING_OPENERS = [
    re.compile(r"^I just received (a|the) (query|prompt|request)[\s\S]{0,200}?\.\s*", re.IGNORECASE),
    re.compile(r"^It seems straightforward[\s\S]{0,200}?\.\s*", re.IGNORECASE),
]

# Precompile common patterns
_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n")
_STRUCTURED_BLOCK = re.compile(r"^\s*(#{1,6}\s|[-*]\s|\d+\.\s|```|[A-Z][A-Z_ ]{2,}:\s*$)")

# Reusable text wrapper (default settings)
_TEXT_WRAPPER = textwrap.TextWrapper(
    width=80,
    break_long_words=False,
    replace_whitespace=False,
)

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

    # Strip common meta-commentary (start only) - use precompiled patterns
    for pat in _META_PREFIXES:
        text = pat.sub("", text).lstrip()

    # If the model dumped "thinking" prose, trim a short generic opener
    # (only at start, only once) - use precompiled patterns
    for pat in _THINKING_OPENERS:
        new_text = pat.sub("", text).lstrip()
        if new_text != text:
            text = new_text
            break

    if not text:
        return ""

    # Split paragraphs - use precompiled pattern
    paragraphs = _PARAGRAPH_SPLIT.split(text)
    cleaned = []

    # Use shared wrapper or create custom one if non-default width
    wrapper = _TEXT_WRAPPER if max_line_length == 80 else textwrap.TextWrapper(
        width=max_line_length,
        break_long_words=False,
        replace_whitespace=False,
    )

    for p in paragraphs:
        p = p.rstrip()
        if not p.strip():
            continue

        # Heuristic: preserve "structured" blocks (headings / bullets / code-ish)
        # Use precompiled pattern
        looks_structured = bool(_STRUCTURED_BLOCK.match(p))
        if looks_structured:
            cleaned.append(p.strip())
            continue

        # Otherwise reflow prose
        p_normalized = " ".join(p.split())
        cleaned.append(wrapper.fill(p_normalized))

    return "\n\n".join(cleaned).strip()
