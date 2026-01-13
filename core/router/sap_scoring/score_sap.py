# 7-Degree SAP Scoring System (Deterministic Heuristics)

import re
from typing import Dict, Any
from functools import lru_cache


from core.config import get_config

# Precompile all regex patterns for performance (avoid recompilation on every scoring call)
# Plausibility patterns
PLAUSIBILITY_CONCRETE = [re.compile(rf'\b{word}\b') for word in
                         ['implement', 'deploy', 'configure', 'test', 'analyze', 'optimize', 'monitor']]
PLAUSIBILITY_TECHNICAL = re.compile(r'\b(algorithm|protocol|system|framework|model|api)\b')
PLAUSIBILITY_VAGUE = [re.compile(rf'\b{word}\b') for word in
                      ['maybe', 'perhaps', 'possibly', 'might', 'could potentially']]

# Utility patterns
UTILITY_BENEFIT = [re.compile(rf'\b{word}\b') for word in
                   ['improve', 'enhance', 'reduce', 'increase', 'solve', 'fix', 'optimize']]
UTILITY_MEASURABLE = re.compile(r'\b(performance|efficiency|accuracy|speed|cost)\b')
UTILITY_IMPACT = re.compile(r'\b(user|system|process|workflow)\b')

# Novelty patterns
NOVELTY_INNOVATIVE = [re.compile(rf'\b{word}\b') for word in
                      ['innovative', 'novel', 'creative', 'experimental', 'new', 'alternative']]
NOVELTY_ADVANCED = re.compile(r'\b(latent|neural|genetic|advanced|sophisticated)\b')
NOVELTY_CONSERVATIVE = [re.compile(rf'\b{word}\b') for word in
                        ['standard', 'traditional', 'conventional', 'typical', 'routine']]

# Risk patterns
RISK_HIGH = [re.compile(rf'\b{word}\b') for word in
             ['experimental', 'unproven', 'untested', 'aggressive', 'radical']]
RISK_BREAKING = re.compile(r'\b(breaking|destructive|irreversible|critical)\b')
RISK_SAFE = [re.compile(rf'\b{word}\b') for word in
             ['validated', 'tested', 'proven', 'stable', 'safe', 'controlled']]

# Alignment patterns
ALIGNMENT_POSITIVE = [re.compile(rf'\b{word}\b') for word in
                      ['safe', 'secure', 'privacy', 'ethical', 'compliant', 'validated']]
ALIGNMENT_AWARENESS = re.compile(r'\b(monitor|audit|review|verify|check)\b')
ALIGNMENT_PENALTY = [re.compile(rf'\b{word}\b') for word in
                     ['bypass', 'override', 'skip', 'ignore']]

# Efficiency patterns
EFFICIENCY_WORDS = [re.compile(rf'\b{word}\b') for word in
                    ['optimize', 'efficient', 'fast', 'lightweight', 'streamline', 'reduce']]
EFFICIENCY_PERFORMANCE = re.compile(r'\b(performance|speed|throughput|latency)\b')
EFFICIENCY_NEGATIVE = re.compile(r'\b(complex|complicated|overhead|redundant|bloat)\b')

# Resilience patterns
RESILIENCE_WORDS = [re.compile(rf'\b{word}\b') for word in
                    ['robust', 'reliable', 'fault-tolerant', 'recovery', 'backup', 'fallback']]
RESILIENCE_BONUS = [re.compile(rf'\b{word}\b') for word in
                    ['validate', 'test', 'rollback', 'monitor']]
RESILIENCE_ERROR = re.compile(r'\b(error|exception|handling|validation|check)\b')
RESILIENCE_FRAGILE = re.compile(r'\b(brittle|fragile|unstable|unreliable)\b')

# Cache scoring calculations (128 most recent unique SAP texts)
@lru_cache(maxsize=128)
def _calculate_plausibility(text_lower: str) -> int:
    """
    Score plausibility based on concrete, actionable language.
    Higher scores for specific technical terms and clear actions.
    """
    score = 5  # baseline

    # Positive indicators
    for pattern in PLAUSIBILITY_CONCRETE:
        if pattern.search(text_lower):
            score += 2

    # Technical specificity
    if PLAUSIBILITY_TECHNICAL.search(text_lower):
        score += 2

    # Negative indicators
    for pattern in PLAUSIBILITY_VAGUE:
        if pattern.search(text_lower):
            score -= 1

    return max(0, min(10, score))


@lru_cache(maxsize=128)
def _calculate_utility(text_lower: str) -> int:
    """
    Score utility based on problem-solving and outcome focus.
    """
    score = 5  # baseline

    # Benefit indicators
    for pattern in UTILITY_BENEFIT:
        if pattern.search(text_lower):
            score += 1

    # Measurable outcomes
    if UTILITY_MEASURABLE.search(text_lower):
        score += 2

    # User/system impact
    if UTILITY_IMPACT.search(text_lower):
        score += 1

    return max(0, min(10, score))


@lru_cache(maxsize=128)
def _calculate_novelty(text_lower: str) -> int:
    """
    Score novelty based on creative/unconventional approaches.
    """
    score = 5  # baseline

    # Innovation indicators
    for pattern in NOVELTY_INNOVATIVE:
        if pattern.search(text_lower):
            score += 2

    # Advanced/cutting-edge terms
    if NOVELTY_ADVANCED.search(text_lower):
        score += 2

    # Conservative indicators (reduce novelty)
    for pattern in NOVELTY_CONSERVATIVE:
        if pattern.search(text_lower):
            score -= 1

    return max(0, min(10, score))


@lru_cache(maxsize=128)
def _calculate_risk(text_lower: str) -> int:
    """
    Score risk level (higher = more risky).
    Will be inverted in final scoring.
    """
    score = 5  # baseline

    # High risk indicators
    for pattern in RISK_HIGH:
        if pattern.search(text_lower):
            score += 2

    # Breaking changes
    if RISK_BREAKING.search(text_lower):
        score += 2

    # Safety indicators (reduce risk)
    for pattern in RISK_SAFE:
        if pattern.search(text_lower):
            score -= 1

    return max(0, min(10, score))


@lru_cache(maxsize=128)
def _calculate_alignment(text_lower: str) -> int:
    """
    Score alignment with safety and ethical considerations.
    """
    score = 5  # baseline

    # Positive alignment indicators
    for pattern in ALIGNMENT_POSITIVE:
        if pattern.search(text_lower):
            score += 2

    # Risk awareness
    if ALIGNMENT_AWARENESS.search(text_lower):
        score += 1

    # Negative alignment indicators (Alignment penalty)
    for pattern in ALIGNMENT_PENALTY:
        if pattern.search(text_lower):
            score -= 3  # Significant penalty

    return max(0, min(10, score))


@lru_cache(maxsize=128)
def _calculate_efficiency(text_lower: str) -> int:
    """
    Score efficiency based on resource optimization.
    """
    score = 5  # baseline

    # Efficiency indicators
    for pattern in EFFICIENCY_WORDS:
        if pattern.search(text_lower):
            score += 1

    # Performance focus
    if EFFICIENCY_PERFORMANCE.search(text_lower):
        score += 2

    # Inefficiency indicators
    if EFFICIENCY_NEGATIVE.search(text_lower):
        score -= 1

    return max(0, min(10, score))


@lru_cache(maxsize=128)
def _calculate_resilience(text_lower: str) -> int:
    """
    Score resilience based on robustness and error handling.
    """
    score = 5  # baseline

    # Resilience indicators
    for pattern in RESILIENCE_WORDS:
        if pattern.search(text_lower):
            score += 2

    # Resilience bonus
    for pattern in RESILIENCE_BONUS:
        if pattern.search(text_lower):
            score += 1

    # Error handling
    if RESILIENCE_ERROR.search(text_lower):
        score += 1

    # Fragility indicators
    if RESILIENCE_FRAGILE.search(text_lower):
        score -= 2

    return max(0, min(10, score))


def score_sap(sap: Dict[str, str]) -> Dict[str, Any]:
    """
    Score a structured SAP dict with title + description using deterministic heuristics.

    Args:
        sap (dict): { title: str, description: str }

    Returns:
        dict: SAP + 7 degrees + composite score

    Scoring dimensions (0-10 each):
        - plausibility: How concrete and actionable
        - utility: Problem-solving value and outcomes
        - novelty: Creative/innovative approach
        - risk: Potential for negative outcomes (inverted: lower risk = higher score)
        - alignment: Safety and ethical considerations
        - efficiency: Resource optimization
        - resilience: Robustness and error handling
    """
    config = get_config()
    full_text = sap['title'] + " - " + sap['description']
    full_text_lower = full_text.lower()

    print(f"Scoring SAP: {sap['title']}")

    # Calculate each dimension using heuristics
    risk_raw = _calculate_risk(full_text_lower)

    degrees = {
        "plausibility": _calculate_plausibility(full_text_lower),
        "utility": _calculate_utility(full_text_lower),
        "novelty": _calculate_novelty(full_text_lower),
        "risk": 10 - risk_raw,  # Invert: lower risk = higher score
        "alignment": _calculate_alignment(full_text_lower),
        "efficiency": _calculate_efficiency(full_text_lower),
        "resilience": _calculate_resilience(full_text_lower),
    }

    # Length penalty application
    length_penalty = 0
    if len(full_text) > 1000:
        length_penalty = 2
    elif len(full_text) > 500:
        length_penalty = 1

    # Apply length penalty to efficiency
    degrees["efficiency"] = max(0, degrees["efficiency"] - length_penalty)

    # Weighted composite score
    weights = config.sap_scoring_weights
    weighted_score = sum(degrees[key] * weights.get(key, 1.0) for key in degrees)

    composite_score = weighted_score

    return {
        **sap,  # Include title + description
        "degrees": degrees,
        "composite_score": round(composite_score, 2)
    }