from langgraph.graph import StateGraph, END
import json
from pathlib import Path

from workflows.state import IncidentState
from analysis.metrics_analysis import analyze_metrics
from analysis.log_analysis import analyze_logs
from reasoning.root_cause_ai import determine_root_cause
from recommendations.recommendation_engine import generate_recommendations
from reporting.report_generator import (
    generate_markdown_report,
    save_markdown,
    markdown_to_pdf
)


# ----------------------
# Workflow Nodes
# ----------------------

def metrics_node(state: IncidentState) -> IncidentState:
    metrics = state["incident"]["metrics_snapshot"]
    state["metrics_analysis"] = analyze_metrics(metrics)
    return state


def logs_node(state: IncidentState) -> IncidentState:
    with open("data/logs/auth-service.log", "r") as f:
        logs = f.readlines()
    state["log_analysis"] = analyze_logs(logs)
    return state


def root_cause_node(state: IncidentState) -> IncidentState:
    state["root_cause"] = determine_root_cause(
        state["metrics_analysis"],
        state["log_analysis"]
    )
    return state


def recommendation_node(state: IncidentState) -> IncidentState:
    print(">>> RECOMMENDATION NODE EXECUTED <<<")

    state["recommendations"] = generate_recommendations(
        state["root_cause"],
        state["incident"]["severity"]
    )
    return state


def report_node(state: IncidentState) -> IncidentState:
    print(">>> REPORT NODE EXECUTED <<<")

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    incident_id = state["incident"]["incident_id"]
    md_path = reports_dir / f"{incident_id}.md"
    pdf_path = reports_dir / f"{incident_id}.pdf"

    # Generate report
    md = generate_markdown_report(state)
    save_markdown(md, md_path)
    markdown_to_pdf(md, str(pdf_path))


    # Update state
    state["report_markdown"] = str(md_path)
    state["report_pdf_path"] = str(pdf_path)

    # Update index.json
    index_path = reports_dir / "index.json"
    if index_path.exists():
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = []

    index.append({
        "incident_id": incident_id,
        "service": state["incident"]["service"],
        "severity": state["incident"]["severity"],
        "detected_at": state["incident"]["detected_at"],
        "md_path": str(md_path),
        "pdf_path": str(pdf_path)
    })

    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

    return state


# ----------------------
# Build Graph
# ----------------------

def build_incident_graph():
    graph = StateGraph(IncidentState)

    graph.add_node("analyze_metrics", metrics_node)
    graph.add_node("analyze_logs", logs_node)
    graph.add_node("root_cause", root_cause_node)
    graph.add_node("recommendations", recommendation_node)
    graph.add_node("report", report_node)

    graph.set_entry_point("analyze_metrics")

    graph.add_edge("analyze_metrics", "analyze_logs")
    graph.add_edge("analyze_logs", "root_cause")
    graph.add_edge("root_cause", "recommendations")
    graph.add_edge("recommendations", "report")
    graph.add_edge("report", END)

    return graph.compile()
