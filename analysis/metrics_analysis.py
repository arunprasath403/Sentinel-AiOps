# analysis/metrics_analysis.py

def analyze_metrics(metrics: dict) -> dict:
    compute = metrics.get("compute", {})
    traffic = metrics.get("traffic", {})
    latency = metrics.get("latency", {})

    analysis = {}

    # CPU
    cpu = compute.get("cpu_percent", {})
    analysis["cpu_status"] = cpu.get("severity", "UNKNOWN")

    # Error rate
    err = traffic.get("error_rate_percent", {})
    analysis["error_rate_status"] = err.get("severity", "UNKNOWN")

    # Latency
    lat = latency.get("latency_ms_p95", {})
    analysis["latency_status"] = lat.get("severity", "UNKNOWN")

    analysis["summary"] = (
        f"CPU: {analysis['cpu_status']}, "
        f"Errors: {analysis['error_rate_status']}, "
        f"Latency: {analysis['latency_status']}"
    )

    return analysis
