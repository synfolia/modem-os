# 7-Degree SAP Scoring System (Deterministic Heuristics)

import re
from typing import Dict, Any


from core.config import get_config

def _calculate_plausibility(text_lower: str) -> int:
    """
    Score plausibility based on concrete, actionable language.
    Higher scores for specific technical terms and clear actions.
    """
    score = 5  # baseline

    # Positive indicators
    concrete_words = ['implement', 'deploy', 'configure', 'test', 'analyze', 'optimize', 'monitor']
    for word in concrete_words:
        if re.search(rf'\b{word}\b', text_lower):
            score += 2

    # Technical specificity
    if re.search(r'\b(algorithm|protocol|system|framework|model|api)\b', text_lower):
        score += 2

    # Negative indicators
    vague_words = ['maybe', 'perhaps', 'possibly', 'might', 'could potentially']
    for word in vague_words:
        if re.search(rf'\b{word}\b', text_lower):
            score -= 1

    return max(0, min(10, score))


def _calculate_utility(text_lower: str) -> int:
    """
    Score utility based on problem-solving and outcome focus.
    """
    score = 5  # baseline

    # Benefit indicators
    benefit_words = ['improve', 'enhance', 'reduce', 'increase', 'solve', 'fix', 'optimize']
    for word in benefit_words:
        if re.search(rf'\b{word}\b', text_lower):
            score += 1

    # Measurable outcomes
    if re.search(r'\b(performance|efficiency|accuracy|speed|cost)\b', text_lower):
        score += 2

    # User/system impact
    if re.search(r'\b(user|system|process|workflow)\b', text_lower):
        score += 1

    return max(0, min(10, score))


def _calculate_novelty(text_lower: str) -> int:
    """
    Score novelty based on creative/unconventional approaches.
    """
    score = 5  # baseline

    # Innovation indicators
    novel_words = ['innovative', 'novel', 'creative', 'experimental', 'new', 'alternative']
    for word in novel_words:
        if re.search(rf'\b{word}\b', text_lower):
            score += 2

    # Advanced/cutting-edge terms
    if re.search(r'\b(latent|neural|genetic|advanced|sophisticated)\b', text_lower):
        score += 2

    # Conservative indicators (reduce novelty)
    conservative_words = ['standard', 'traditional', 'conventional', 'typical', 'routine']
    for word in conservative_words:
        if re.search(rf'\b{word}\b', text_lower):
            score -= 1

    return max(0, min(10, score))


def _calculate_risk(text_lower: str) -> int:
    """
    Score risk level (higher = more risky).
    Will be inverted in final scoring.
    """
    score = 5  # baseline

    # High risk indicators
    risky_words = ['experimental', 'unproven', 'untested', 'aggressive', 'radical']
    for word in risky_words:
        if re.search(rf'\b{word}\b', text_lower):
            score += 2

    # Breaking changes
    if re.search(r'\b(breaking|destructive|irreversible|critical)\b', text_lower):
        score += 2

    # Safety indicators (reduce risk)
    safe_words = ['validated', 'tested', 'proven', 'stable', 'safe', 'controlled']
    for word in safe_words:
        if re.search(rf'\b{word}\b', text_lower):
            score -= 1

    return max(0, min(10, score))


def _calculate_alignment(text_lower: str) -> int:
    """
    Score alignment with safety and ethical considerations.
    """
    score = 5  # baseline

    # Positive alignment indicators
    aligned_words = ['safe', 'secure', 'privacy', 'ethical', 'compliant', 'validated']
    for word in aligned_words:
        if re.search(rf'\b{word}\b', text_lower):
            score += 2

    # Risk awareness
    if re.search(r'\b(monitor|audit|review|verify|check)\b', text_lower):
        score += 1

    # Negative alignment indicators (Alignment penalty)
    penalty_words = ['bypass', 'override', 'skip', 'ignore']
    for word in penalty_words:
        if re.search(rf'\b{word}\b', text_lower):
            score -= 3 # Significant penalty

    return max(0, min(10, score))


def _calculate_efficiency(text_lower: str) -> int:
    """
    Score efficiency based on resource optimization.
    """
    score = 5  # baseline

    # Efficiency indicators
    efficient_words = ['optimize', 'efficient', 'fast', 'lightweight', 'streamline', 'reduce']
    for word in efficient_words:
        if re.search(rf'\b{word}\b', text_lower):
            score += 1

    # Performance focus
    if re.search(r'\b(performance|speed|throughput|latency)\b', text_lower):
        score += 2

    # Inefficiency indicators
    if re.search(r'\b(complex|complicated|overhead|redundant|bloat)\b', text_lower):
        score -= 1

    return max(0, min(10, score))


def _calculate_resilience(text_lower: str) -> int:
    """
    Score resilience based on robustness and error handling.
    """
    score = 5  # baseline

    # Resilience indicators
    resilient_words = ['robust', 'reliable', 'fault-tolerant', 'recovery', 'backup', 'fallback']
    for word in resilient_words:
        if re.search(rf'\b{word}\b', text_lower):
            score += 2

    # Resilience bonus
    bonus_words = ['validate', 'test', 'rollback', 'monitor']
    for word in bonus_words:
        if re.search(rf'\b{word}\b', text_lower):
            score += 1

    # Error handling
    if re.search(r'\b(error|exception|handling|validation|check)\b', text_lower):
        score += 1

    # Fragility indicators
    if re.search(r'\b(brittle|fragile|unstable|unreliable)\b', text_lower):
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