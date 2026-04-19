def calculate_risk(headers, https_status):
    risk_score = 0

    # HTTPS
    if https_status != "SECURE":
        risk_score += 50

    # Headers
    missing = sum(1 for h in headers.values() if h == "MISSING")
    risk_score += missing * 10

    if risk_score >= 70:
        return "HIGH"
    elif risk_score >= 40:
        return "MEDIUM"
    else:
        return "LOW"