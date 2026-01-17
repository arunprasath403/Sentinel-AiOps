from datetime import datetime
from typing import Dict, Any, List
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def generate_markdown_report(state: Dict[str, Any]) -> str:
    incident = state["incident"]
    metrics = state["metrics_analysis"]
    logs = state["log_analysis"]
    recommendations = state["recommendations"]

    lines: List[str] = []

    lines.append(f"# Incident Report — {incident['incident_id']}\n")

    # Summary
    lines.append("## Incident Summary")
    lines.append(f"- **Service:** {incident['service']}")
    lines.append(f"- **Severity:** {incident['severity']}")
    lines.append(f"- **Detected At:** {incident['detected_at']}")
    lines.append(f"- **Symptoms:** {', '.join(incident['symptoms'])}\n")

    # Metrics
    lines.append("## Metrics Analysis")
    for k, v in metrics.items():
        lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
    lines.append("")

    # Logs
    lines.append("## Log Analysis")
    lines.append(f"- **Error Count:** {logs['error_count']}")
    lines.append(f"- **Warning Count:** {logs['warning_count']}")
    lines.append("- **Key Errors:**")
    for err in logs["key_errors"]:
        lines.append(f"  - {err}")
    lines.append("")

    # Root Cause
    lines.append("## Root Cause")
    lines.append(state["root_cause"])
    lines.append("")

    # Recommendations
    lines.append("## Recommended Actions")
    for r in recommendations:
        lines.append(
            f"- **{r['action']}** "
            f"(type: {r['type']}, confidence: {r['confidence']})  \n"
            f"  _{r['explanation']}_"
        )

    lines.append("\n---")
    lines.append(f"_Report generated on {datetime.utcnow().isoformat()}Z_")

    return "\n".join(lines)


def save_markdown(md: str, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)



def markdown_to_pdf(md_text: str, pdf_path: str):
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=16,
        alignment=TA_LEFT
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=6
    )

    italic_style = ParagraphStyle(
        "ItalicStyle",
        parent=styles["Normal"],
        fontSize=9,
        spaceAfter=8,
        fontName="Helvetica-Oblique"
    )

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []

    for line in md_text.split("\n"):
        line = line.strip()

        if not line:
            story.append(Spacer(1, 10))
            continue

        # Title
        if line.startswith("# "):
            story.append(Paragraph(line.replace("# ", ""), title_style))

        # Section headers
        elif line.startswith("## "):
            story.append(Spacer(1, 12))
            story.append(Paragraph(line.replace("## ", ""), heading_style))

        # Bullet points
        elif line.startswith("- "):
            story.append(
                Paragraph("• " + line.replace("- ", ""), body_style)
            )

        # Italic notes
        elif line.startswith("_") and line.endswith("_"):
            story.append(
                Paragraph(line.strip("_"), italic_style)
            )

        # Normal text
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
