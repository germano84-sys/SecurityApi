from fastapi import FastAPI
from scanner.endpoints import get_endpoints
from scanner.headers import analyze_headers
from scanner.https_check import check_https
from crypto.encrypt import encrypt_text, decrypt_text
from crypto.hash import hash_sha256, hash_bcrypt
from core.risk import calculate_risk
from database.database import init_db, save_scan
init_db()

# ======================
#0. NOMBRE APP
# ======================
app = FastAPI(title="SecureAPI - Escáner de Vulnerabilidades y Cifrado",
    description="API para análisis de seguridad web (cabeceras, endpoints, HTTPS) y servicios de cifrado y hashing.",
    version="1.0.0")

# ======================
# 1. SCANNER Y GUARDAR INFORMACIÓN
# ======================
@app.get("/escanear", summary="Escanear sitio web")
def escanear(url: str):
    endpoints = get_endpoints(url)
    headers = analyze_headers(url)
    https_status = check_https(url)
    risk = calculate_risk(headers, https_status)

   #Guardar en BD
    save_scan(url, endpoints, headers, https_status, risk)

    return {
        "url": url,
        "endpoints_encontrados": endpoints,
        "cabeceras": headers,
        "seguridad_https": https_status,
        "nivel_riesgo": risk
    }

# ======================
# 2. CRYPTO
# ======================
@app.post("/encriptar", summary="Encriptar texto")
def encriptar(data: str):
    return {"encriptado": encrypt_text(data)}

@app.post("/desencriptar", summary="Desencriptar texto")
def desencriptar(data: str):
    return {"desencriptado": decrypt_text(data)}

@app.post("/hash/sha256", summary="Generar hash SHA256")
def sha256(data: str):
    return {"hash": hash_sha256(data)}

@app.post("/hash/bcrypt", summary="Generar hash bcrypt")
def bcrypt_hash(data: str):
    return {"hash": hash_bcrypt(data)}

# ======================
# 3. ENDPOINT PARA VER EL HISTORIAL
# ======================
import sqlite3

@app.get("/historial", summary="Ver historial de escaneos")
def historial():
    conn = sqlite3.connect("scans.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans")
    rows = cursor.fetchall()
    conn.close()
    return {"registros": rows}