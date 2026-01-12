import re
import textwrap

def clean_output(text: str, max_line_length: int = 80) -> str:
    """
    Normalizes output text by:
    1. Normalizing whitespace (preserving paragraphs).
    2. Stripping common meta-commentary.
    3. Limiting line length.
    """
    if not text:
        return ""

    # Strip leading/trailing whitespace
    text = text.strip()

    # Strip common meta-commentary (start of text)
    meta_patterns = [
        r"^Here is the .*?:",
        r"^Sure, here is .*?:",
        r"^I can help with that[\.:]",
        r"^Okay, .*?[\.:]",
        r"^Below is .*?[\.:]",
        r"^Certainly! .*?[\.:]",
    ]

    for pattern in meta_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE).strip()

    # Preserve paragraphs (split by double newlines)
    paragraphs = re.split(r'\n\s*\n', text)
    cleaned_paragraphs = []

    wrapper = textwrap.TextWrapper(width=max_line_length, break_long_words=False, replace_whitespace=False)

    for p in paragraphs:
        if not p.strip():
            continue
        # Normalize internal whitespace of the paragraph (replace single newlines with space)
        # This reflows the paragraph.
        p_normalized = " ".join(p.split())
        cleaned_paragraphs.append(wrapper.fill(p_normalized))

    return "\n\n".join(cleaned_paragraphs)
