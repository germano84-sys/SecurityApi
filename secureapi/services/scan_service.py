from core.risk import calculate_risk
from repositories.scan_repository import save_scan
from scanner.endpoints import get_endpoints
from scanner.headers import analyze_headers
from scanner.https_check import check_https


def scan_url(url: str):
    endpoints = get_endpoints(url)
    headers = analyze_headers(url)
    https_status = check_https(url)
    risk = calculate_risk(headers, https_status)

    save_scan(url, endpoints, headers, https_status, risk)

    return {
        "url": url,
        "endpoints_encontrados": endpoints,
        "cabeceras": headers,
        "seguridad_https": https_status,
        "nivel_riesgo": risk,
    }
