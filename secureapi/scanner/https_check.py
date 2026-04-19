import ssl
import socket
from urllib.parse import urlparse

def check_https(url):
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname

        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname):
                return "SECURE"

    except Exception:
        return "NOT SECURE"