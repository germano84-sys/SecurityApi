from secureapi.core.risk import calculate_risk
from secureapi.repositories.scan_repository import save_scan
from secureapi.scanner.endpoints import get_endpoints
from secureapi.scanner.headers import analyze_headers
from secureapi.scanner.https_check import check_https
from secureapi.services.notification_service import notify_scan_completed


def build_vulnerabilities(headers, https_status, endpoints):
    vulnerabilities = []

    if https_status != "SECURE":
        vulnerabilities.append("HTTPS no es seguro o el certificado no se pudo validar")

    if isinstance(headers, dict):
        if headers.get("error"):
            vulnerabilities.append(f"No se pudieron analizar cabeceras: {headers['error']}")
        else:
            for name, status in headers.items():
                if name.startswith("_"):
                    continue
                if status == "MISSING":
                    vulnerabilities.append(f"Cabecera de seguridad faltante: {name}")
                elif status == "WEAK":
                    vulnerabilities.append(f"Cabecera de seguridad debil: {name}")
                elif status == "INVALID":
                    vulnerabilities.append(f"Cabecera de seguridad invalida: {name}")
    else:
        vulnerabilities.append("Resultado invalido en analisis de cabeceras")

    if isinstance(endpoints, dict) and endpoints.get("error"):
        vulnerabilities.append(f"No se pudieron recolectar endpoints: {endpoints['error']}")

    return vulnerabilities


def scan_url_for_user(url: str, current_user: dict):
    endpoints = get_endpoints(url)
    headers = analyze_headers(url)
    https_status = check_https(url)
    risk = calculate_risk(headers, https_status)
    vulnerabilities = build_vulnerabilities(headers, https_status, endpoints)

    save_scan(
        url,
        endpoints,
        headers,
        https_status,
        risk,
        performed_by=current_user["id"],
        performed_by_username=current_user["username"],
    )

    scan_result = {
        "url": url,
        "usuario": current_user["username"],
        "endpoints_encontrados": endpoints,
        "cabeceras": headers,
        "seguridad_https": https_status,
        "nivel_riesgo": risk,
        "vulnerabilidades_detectadas": vulnerabilities,
    }

    notify_scan_completed(scan_result)
    return scan_result
