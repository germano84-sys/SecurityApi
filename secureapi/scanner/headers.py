from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException, SSLError


REQUEST_HEADERS = {
    "User-Agent": "SecureAPI-Scanner/1.0",
}


def _normalize_url(raw_url: str) -> str:
    url = (raw_url or "").strip()
    if "://" not in url:
        return f"https://{url}"
    return url


def _evaluate_hsts(value: str) -> str:
    if not value:
        return "MISSING"

    lowered = value.lower()
    if "max-age=" not in lowered:
        return "INVALID"

    try:
        max_age_token = [token for token in lowered.split(";") if "max-age=" in token][0]
        max_age = int(max_age_token.split("=")[1].strip())
    except (IndexError, ValueError):
        return "INVALID"

    if max_age < 31536000:
        return "WEAK"
    return "OK"


def _evaluate_x_frame_options(value: str) -> str:
    if not value:
        return "MISSING"
    lowered = value.strip().lower()
    if lowered in {"deny", "sameorigin"}:
        return "OK"
    return "WEAK"


def _evaluate_x_content_type_options(value: str) -> str:
    if not value:
        return "MISSING"
    return "OK" if value.strip().lower() == "nosniff" else "WEAK"


def _evaluate_csp(value: str) -> str:
    if not value:
        return "MISSING"
    lowered = value.lower()
    if "unsafe-inline" in lowered or "unsafe-eval" in lowered:
        return "WEAK"
    return "OK"


def _request_with_fallback(url: str):
    meta = {
        "requested_url": url,
        "tls_verification": "strict",
        "used_fallback": False,
    }

    try:
        response = requests.get(url, timeout=8, allow_redirects=True, headers=REQUEST_HEADERS)
        return response, meta
    except SSLError as ssl_error:
        # Force a second pass without TLS verification to still collect headers.
        meta["tls_verification"] = "disabled-for-scan"
        meta["used_fallback"] = True
        meta["tls_error"] = str(ssl_error)
        try:
            response = requests.get(
                url,
                timeout=8,
                allow_redirects=True,
                headers=REQUEST_HEADERS,
                verify=False,
            )
            return response, meta
        except RequestException as fallback_error:
            meta["fallback_error"] = str(fallback_error)
            return None, meta
    except RequestException as request_error:
        # If caller forgot scheme or URL is HTTP-only, retry through http.
        parsed = urlparse(url)
        if parsed.scheme.lower() == "https":
            http_url = url.replace("https://", "http://", 1)
            meta["used_fallback"] = True
            meta["fallback_protocol"] = "http"
            try:
                response = requests.get(
                    http_url,
                    timeout=8,
                    allow_redirects=True,
                    headers=REQUEST_HEADERS,
                )
                meta["requested_url"] = http_url
                return response, meta
            except RequestException as http_error:
                meta["fallback_error"] = str(http_error)
                meta["error"] = str(request_error)
                return None, meta

        meta["error"] = str(request_error)
        return None, meta


def analyze_headers(url):
    normalized_url = _normalize_url(url)
    response, meta = _request_with_fallback(normalized_url)
    if response is None:
        return {
            "error": meta.get("fallback_error") or meta.get("error") or "No se pudo obtener respuesta",
            "_meta": meta,
        }

    headers = response.headers
    report = {
        "Strict-Transport-Security": _evaluate_hsts(headers.get("Strict-Transport-Security", "")),
        "Content-Security-Policy": _evaluate_csp(headers.get("Content-Security-Policy", "")),
        "X-Frame-Options": _evaluate_x_frame_options(headers.get("X-Frame-Options", "")),
        "X-Content-Type-Options": _evaluate_x_content_type_options(headers.get("X-Content-Type-Options", "")),
        "_meta": {
            **meta,
            "status_code": response.status_code,
            "final_url": response.url,
        },
    }
    return report