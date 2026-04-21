import ssl
import socket
from urllib.parse import urlparse


def _normalize_url(raw_url):
    raw_url = (raw_url or "").strip()
    if "://" not in raw_url:
        raw_url = f"https://{raw_url}"
    return raw_url


def check_https(url):
    try:
        parsed = urlparse(_normalize_url(url))
        hostname = parsed.hostname
        if not hostname:
            return "NOT SECURE"

        # Explicit HTTP is not considered secure.
        if parsed.scheme and parsed.scheme.lower() == "http":
            return "NOT SECURE"

        port = parsed.port or 443

        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname):
                return "SECURE"

    except Exception:
        return "NOT SECURE"