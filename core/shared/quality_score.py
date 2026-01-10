import re

_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")
_ROUTER_ERR_RE = re.compile(r"\bRouter error\b|Connection refused|Max retries exceeded", re.IGNORECASE)
_CHATTER_RE = re.compile(r"\b(how can i help|happy to help|no worries|glad to help|😊|🙂)\b", re.IGNORECASE)
_TECH_RE = re.compile(r"\b(inference|latency|compute|token|model|planning|optimization|gradient|policy|reward|search|memory|routing)\b", re.IGNORECASE)
_TRADEOFF_RE = re.compile(r"\b(tradeoff|limitation|however|but|drawback|cost)\b", re.IGNORECASE)

def quality_score(text: str) -> dict:
    """
    Returns quality metrics for a trace result.
    quality: 0..100
    """
    t = (text or "").strip()

    # Fail fast
    if not t:
        return {"quality": 0, "reason": "empty"}
    if _ROUTER_ERR_RE.search(t):
        return {"quality": 3, "reason": "router_error"}

    score = 50  # start neutral

    # Length shaping (sweet spot ~ 80..900 chars)
    n = len(t)
    if n < 80:
        score -= 20
    elif n < 200:
        score -= 5
    elif n > 2500:
        score -= 10

    # Structure bonus
    lines = t.splitlines()
    bullet_lines = sum(1 for line in lines if line.lstrip().startswith(("-", "*")) or re.match(r"^\s*\d+\.", line))
    if bullet_lines >= 3:
        score += 10
    if "###" in t or "\n##" in t:
        score += 5

    # Technical density
    tech_hits = len(_TECH_RE.findall(t))
    score += min(tech_hits * 2, 12)

    # Mentions tradeoffs/limitations
    if _TRADEOFF_RE.search(t):
        score += 8

    # Penalize chatty tone
    if _EMOJI_RE.search(t):
        score -= 12
    if _CHATTER_RE.search(t):
        score -= 12
    exclaims = t.count("!")
    score -= min(exclaims * 2, 10)

    # Clamp
    score = max(0, min(100, score))

    return {
        "quality": int(score),
        "len_chars": n,
        "bullets": bullet_lines,
        "tech_hits": tech_hits,
        "has_tradeoff": bool(_TRADEOFF_RE.search(t)),
    }
