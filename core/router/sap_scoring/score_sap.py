# 7-Degree SAP Scoring System (Deterministic Heuristics)

import re
from typing import Dict, Any


def _calculate_plausibility(text: str) -> int:
    """
    Score plausibility based on concrete, actionable language.
    Higher scores for specific technical terms and clear actions.
    """
    score = 5  # baseline

    # Positive indicators
    concrete_words = ['implement', 'deploy', 'configure', 'test', 'analyze', 'optimize', 'monitor']
    score += sum(2 for word in concrete_words if word in text.lower())

    # Technical specificity
    if re.search(r'\b(algorithm|protocol|system|framework|model|api)\b', text.lower()):
        score += 2

    # Negative indicators
    vague_words = ['maybe', 'perhaps', 'possibly', 'might', 'could potentially']
    score -= sum(1 for word in vague_words if word in text.lower())

    return max(0, min(10, score))


def _calculate_utility(text: str) -> int:
    """
    Score utility based on problem-solving and outcome focus.
    """
    score = 5  # baseline

    # Benefit indicators
    benefit_words = ['improve', 'enhance', 'reduce', 'increase', 'solve', 'fix', 'optimize']
    score += sum(1 for word in benefit_words if word in text.lower())

    # Measurable outcomes
    if re.search(r'\b(performance|efficiency|accuracy|speed|cost)\b', text.lower()):
        score += 2

    # User/system impact
    if re.search(r'\b(user|system|process|workflow)\b', text.lower()):
        score += 1

    return max(0, min(10, score))


def _calculate_novelty(text: str) -> int:
    """
    Score novelty based on creative/unconventional approaches.
    """
    score = 5  # baseline

    # Innovation indicators
    novel_words = ['innovative', 'novel', 'creative', 'experimental', 'new', 'alternative']
    score += sum(2 for word in novel_words if word in text.lower())

    # Advanced/cutting-edge terms
    if re.search(r'\b(latent|neural|genetic|advanced|sophisticated)\b', text.lower()):
        score += 2

    # Conservative indicators (reduce novelty)
    conservative_words = ['standard', 'traditional', 'conventional', 'typical', 'routine']
    score -= sum(1 for word in conservative_words if word in text.lower())

    return max(0, min(10, score))


def _calculate_risk(text: str) -> int:
    """
    Score risk level (higher = more risky).
    Will be inverted in final scoring.
    """
    score = 5  # baseline

    # High risk indicators
    risky_words = ['experimental', 'unproven', 'untested', 'aggressive', 'radical']
    score += sum(2 for word in risky_words if word in text.lower())

    # Breaking changes
    if re.search(r'\b(breaking|destructive|irreversible|critical)\b', text.lower()):
        score += 2

    # Safety indicators (reduce risk)
    safe_words = ['validated', 'tested', 'proven', 'stable', 'safe', 'controlled']
    score -= sum(1 for word in safe_words if word in text.lower())

    return max(0, min(10, score))


def _calculate_alignment(text: str) -> int:
    """
    Score alignment with safety and ethical considerations.
    """
    score = 5  # baseline

    # Positive alignment indicators
    aligned_words = ['safe', 'secure', 'privacy', 'ethical', 'compliant', 'validated']
    score += sum(2 for word in aligned_words if word in text.lower())

    # Risk awareness
    if re.search(r'\b(monitor|audit|review|verify|check)\b', text.lower()):
        score += 1

    # Negative alignment indicators
    if re.search(r'\b(bypass|skip|override|ignore)\b', text.lower()):
        score -= 2

    return max(0, min(10, score))


def _calculate_efficiency(text: str) -> int:
    """
    Score efficiency based on resource optimization.
    """
    score = 5  # baseline

    # Efficiency indicators
    efficient_words = ['optimize', 'efficient', 'fast', 'lightweight', 'streamline', 'reduce']
    score += sum(1 for word in efficient_words if word in text.lower())

    # Performance focus
    if re.search(r'\b(performance|speed|throughput|latency)\b', text.lower()):
        score += 2

    # Inefficiency indicators
    if re.search(r'\b(complex|complicated|overhead|redundant|bloat)\b', text.lower()):
        score -= 1

    return max(0, min(10, score))


def _calculate_resilience(text: str) -> int:
    """
    Score resilience based on robustness and error handling.
    """
    score = 5  # baseline

    # Resilience indicators
    resilient_words = ['robust', 'reliable', 'fault-tolerant', 'recovery', 'backup', 'fallback']
    score += sum(2 for word in resilient_words if word in text.lower())

    # Error handling
    if re.search(r'\b(error|exception|handling|validation|check)\b', text.lower()):
        score += 1

    # Fragility indicators
    if re.search(r'\b(brittle|fragile|unstable|unreliable)\b', text.lower()):
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

    composite_score = sum(degrees.values())

    return {
        **sap,  # Include title + description
        "degrees": degrees,
        "composite_score": composite_score
    }