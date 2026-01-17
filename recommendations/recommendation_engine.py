# recommendations/recommendation_engine.py

from typing import List, Dict
from reasoning.root_cause_ai import client

# ----------------------
# Allowed Actions (Deterministic)
# ----------------------

ALLOWED_ACTIONS = {
    "database_connectivity": [
        {
            "action": "Check database connection pool saturation",
            "type": "INVESTIGATE",
            "base_confidence": 0.85
        },
        {
            "action": "Verify database network connectivity",
            "type": "INVESTIGATE",
            "base_confidence": 0.80
        },
        {
            "action": "Scale database read replicas",
            "type": "MITIGATE",
            "base_confidence": 0.65
        }
    ],
    "unknown": [
        {
            "action": "Collect additional metrics and logs",
            "type": "INVESTIGATE",
            "base_confidence": 0.50
        }
    ]
}

# ----------------------
# Root Cause Classification
# ----------------------

def classify_root_cause(root_cause: str) -> str:
    rc = root_cause.lower()
    if any(k in rc for k in ["database", "db", "sql", "connection"]):
        return "database_connectivity"
    return "unknown"

# ----------------------
# Confidence Adjustment
# ----------------------

def adjust_confidence(base: float, severity: str) -> float:
    if severity == "CRITICAL":
        return round(min(base + 0.10, 0.98), 2)
    if severity == "HIGH":
        return round(min(base + 0.05, 0.95), 2)
    return round(base, 2)

# ----------------------
# Shared AI Explanation
# ----------------------

def generate_shared_explanation(root_cause: str) -> str:
    prompt = f"""
You are an SRE assistant.

Explain the root cause below in ONE concise sentence.
Do NOT suggest actions.

Root cause: {root_cause}
"""
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Explanation unavailable due to AI service error"

# ----------------------
# Recommendation Engine
# ----------------------

def generate_recommendations(root_cause: str, severity: str) -> List[Dict]:
    category = classify_root_cause(root_cause)
    actions = ALLOWED_ACTIONS.get(category, ALLOWED_ACTIONS["unknown"])

    explanation = generate_shared_explanation(root_cause)

    recommendations = []

    for item in actions:
        recommendations.append({
            "action": item["action"],
            "type": item["type"],
            "confidence": adjust_confidence(item["base_confidence"], severity),
            "explanation": explanation
        })

    return recommendations
