# 7-Degree SAP Scoring System (DeepSeek version)

import random

def score_sap(sap):
    """
    Score a structured SAP dict with title + description.

    Args:
        sap (dict): { title: ..., description: ... }

    Returns:
        dict: SAP + 7 degrees + composite score
    """
    full_text = sap['title'] + " - " + sap['description']

    print(f"Scoring SAP: {sap['title']}")

    degrees = {
        "plausibility": random.randint(0, 10),
        "utility": random.randint(0, 10),
        "novelty": random.randint(0, 10),
        "risk": random.randint(0, 10),
        "alignment": random.randint(0, 10),
        "efficiency": random.randint(0, 10),
        "resilience": random.randint(0, 10),
    }
    degrees["risk"] = 10 - degrees["risk"]

    composite_score = sum(degrees.values())

    return {
        **sap,  # Include title + description
        "degrees": degrees,
        "composite_score": composite_score
    }