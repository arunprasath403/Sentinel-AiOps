from typing import TypedDict, Dict, List, Any


class IncidentState(TypedDict):
    incident: Dict[str, Any]
    metrics_analysis: Dict[str, Any]
    log_analysis: Dict[str, Any]
    root_cause: str
    recommendations: List[Dict[str, Any]]
    report_markdown: str
    report_pdf_path: str
