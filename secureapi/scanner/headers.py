import requests

def analyze_headers(url):
    try:
        res = requests.get(url, timeout=5)
        headers = res.headers

        security_headers = [
            "X-Frame-Options",
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Content-Type-Options"
        ]

        report = {}
        for h in security_headers:
            report[h] = "OK" if h in headers else "MISSING"

        return report

    except Exception as e:
        return {"error": str(e)}