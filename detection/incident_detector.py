# detection/incident_detector.py

import json
from uuid import uuid4
from datetime import datetime

SEVERITY_SCORE = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3
}


def detect_incident(metrics_path: str):
    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    symptoms = []
    severity_scores = []

    def walk(obj, prefix=""):
        for k, v in obj.items():
            if isinstance(v, dict) and "severity" in v and "value" in v:
                sev = v["severity"]
                severity_scores.append(SEVERITY_SCORE[sev])

                if SEVERITY_SCORE[sev] >= 2:
                    name = f"{prefix}{k}".replace("_", " ").title()
                    symptoms.append(f"{name} is {sev}")

            elif isinstance(v, dict):
                walk(v, prefix=f"{k} ")

    walk(metrics)

    if not severity_scores or max(severity_scores) < 2:
        return None

    max_sev = max(severity_scores)
    severity_label = {v: k for k, v in SEVERITY_SCORE.items()}[max_sev]

    return {
        "incident_id": f"INC-{uuid4().hex[:6].upper()}",
        "service": metrics["service"],
        "severity": severity_label,
        "detected_at": datetime.utcnow().isoformat() + "Z",
        "symptoms": symptoms,
        "metrics_snapshot": metrics
    }


if __name__ == "__main__":
    incident = detect_incident("data/metrics/service_metrics.json")
    if incident:
        print(json.dumps(incident, indent=2))
    else:
        print("No incident detected")
