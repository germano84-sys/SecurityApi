import smtplib
from email.mime.text import MIMEText
from pathlib import Path

from secureapi.core.config import (
    EMAIL_FROM,
    EMAIL_NOTIFICATIONS_ENABLED,
    EMAIL_SMTP_HOST,
    EMAIL_SMTP_PASSWORD,
    EMAIL_SMTP_PORT,
    EMAIL_SMTP_USE_TLS,
    EMAIL_SMTP_USER,
    EMAIL_SUBJECT_PREFIX,
    EMAIL_TO,
    FCM_DEVICE_TOKEN,
    FCM_ENABLED,
    FIREBASE_SERVICE_ACCOUNT_PATH,
)

_FIREBASE_INITIALIZED = False
_RUNTIME_FCM_DEVICE_TOKEN = (FCM_DEVICE_TOKEN or "").strip()


def _effective_fcm_device_token() -> str:
    return (_RUNTIME_FCM_DEVICE_TOKEN or FCM_DEVICE_TOKEN or "").strip()


def set_runtime_fcm_device_token(token: str) -> dict:
    global _RUNTIME_FCM_DEVICE_TOKEN

    _RUNTIME_FCM_DEVICE_TOKEN = (token or "").strip()
    preview = ""
    if _RUNTIME_FCM_DEVICE_TOKEN:
        preview = f"{_RUNTIME_FCM_DEVICE_TOKEN[:12]}...{_RUNTIME_FCM_DEVICE_TOKEN[-8:]}"

    return {
        "message": "Token FCM actualizado",
        "token_preview": preview,
    }


def _parse_recipients(raw_recipients: str) -> list[str]:
    if not raw_recipients:
        return []

    normalized = raw_recipients.replace(";", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _build_scan_summary(scan_result: dict) -> str:
    vulnerabilities = scan_result.get("vulnerabilidades_detectadas") or []
    vulnerabilities_text = "\n".join(f"- {item}" for item in vulnerabilities) or "- Sin vulnerabilidades detectadas"

    return (
        "Resultado automatico de escaneo SecurityApi\n\n"
        f"URL: {scan_result.get('url')}\n"
        f"Usuario: {scan_result.get('usuario', 'N/A')}\n"
        f"Seguridad HTTPS: {scan_result.get('seguridad_https')}\n"
        f"Nivel de riesgo: {scan_result.get('nivel_riesgo')}\n\n"
        "Vulnerabilidades:\n"
        f"{vulnerabilities_text}\n"
    )


def send_scan_email(scan_result: dict) -> bool:
    if not EMAIL_NOTIFICATIONS_ENABLED:
        return False

    recipients = _parse_recipients(EMAIL_TO)
    required_values = [EMAIL_SMTP_HOST, EMAIL_FROM]
    if not all(required_values):
        return False
    if not recipients:
        return False

    message = MIMEText(_build_scan_summary(scan_result), "plain", "utf-8")
    message["Subject"] = f"[{EMAIL_SUBJECT_PREFIX}] Escaneo de {scan_result.get('url', 'sitio')}"
    message["From"] = EMAIL_FROM
    message["To"] = ", ".join(recipients)

    with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=15) as smtp:
        smtp.ehlo()
        if EMAIL_SMTP_USE_TLS:
            smtp.starttls()
            smtp.ehlo()
        if EMAIL_SMTP_USER:
            smtp.login(EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD)
        smtp.sendmail(EMAIL_FROM, recipients, message.as_string())

    return True


def _get_firebase_messaging_module():
    global _FIREBASE_INITIALIZED

    # Delay import so the app still runs even when Firebase is not configured.
    import firebase_admin
    from firebase_admin import credentials, messaging

    if not _FIREBASE_INITIALIZED:
        service_account_path = Path(FIREBASE_SERVICE_ACCOUNT_PATH)
        if not service_account_path.exists():
            raise FileNotFoundError("FIREBASE_SERVICE_ACCOUNT_PATH no existe")

        firebase_admin.initialize_app(credentials.Certificate(str(service_account_path)))
        _FIREBASE_INITIALIZED = True

    return messaging


def send_scan_fcm_notification(scan_result: dict) -> bool:
    fcm_token = _effective_fcm_device_token()
    if not FCM_ENABLED or not fcm_token:
        return False

    messaging = _get_firebase_messaging_module()
    notification = messaging.Notification(
        title="SecurityApi - Escaneo ejecutado",
        body=f"{scan_result.get('url')} | Riesgo: {scan_result.get('nivel_riesgo')}",
    )

    data_payload = {
        "url": str(scan_result.get("url", "")),
        "riesgo": str(scan_result.get("nivel_riesgo", "")),
        "https": str(scan_result.get("seguridad_https", "")),
    }

    message = messaging.Message(
        notification=notification,
        data=data_payload,
        token=fcm_token,
    )
    messaging.send(message)
    return True


def notify_scan_completed(scan_result: dict) -> dict:
    result = {
        "email_sent": False,
        "fcm_sent": False,
        "email_error": None,
        "fcm_error": None,
    }

    try:
        result["email_sent"] = send_scan_email(scan_result)
    except Exception as exc:
        result["email_error"] = str(exc)

    try:
        result["fcm_sent"] = send_scan_fcm_notification(scan_result)
    except Exception as exc:
        result["fcm_error"] = str(exc)

    return result
