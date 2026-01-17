from detection.incident_detector import detect_incident
from workflows.incident_graph import build_incident_graph
import json

incident = detect_incident("data/metrics/service_metrics.json")

if incident is None:
    print("No incident detected. Workflow skipped.")
    exit(0)

state = {
    "incident": incident,
    "metrics_analysis": {},
    "log_analysis": {},
    "root_cause": "",
    "recommendations": []
}

graph = build_incident_graph()
final_state = graph.invoke(state)

with open("dashboard/latest_incident.json", "w") as f:
    json.dump(final_state, f, indent=2)
