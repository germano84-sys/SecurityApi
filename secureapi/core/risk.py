def calculate_risk(headers, https_status):
    risk_score = 0

    # HTTPS
    if https_status != "SECURE":
        risk_score += 50

    # Header scan failure should increase risk significantly.
    if not isinstance(headers, dict) or headers.get("error"):
        risk_score += 40
    else:
        header_statuses = [
            status
            for key, status in headers.items()
            if not key.startswith("_") and isinstance(status, str)
        ]
        missing = sum(1 for status in header_statuses if status == "MISSING")
        weak = sum(1 for status in header_statuses if status == "WEAK")
        invalid = sum(1 for status in header_statuses if status == "INVALID")
        unknown = sum(1 for status in header_statuses if status == "UNKNOWN")

        risk_score += (missing * 12) + (invalid * 12) + (weak * 6) + (unknown * 8)

    if risk_score >= 70:
        return "HIGH"
    elif risk_score >= 40:
        return "MEDIUM"
    else:
        return "LOW"