import warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import requests
import json
import subprocess
from dotenv import load_dotenv
import os


# Cargar variables del entorno (.env)
load_dotenv()

# Configuración base
JIRA_URL = os.getenv("JIRA_URL")
JIRA_ISSUE = os.getenv("JIRA_ISSUE")
JIRA_COOKIE = os.getenv("JIRA_COOKIE")

# ⚠️ Sustituye los valores de las cookies por los tuyos (copiados desde Chrome)
headers = {
    "Cookie": JIRA_COOKIE,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def probar_conexion_cookie():
    """Prueba acceso al issue usando cookies de sesión"""
    url = f"{JIRA_URL}/rest/api/3/issue/{JIRA_ISSUE}"
    print(f"🔎 Probando acceso a: {url}")
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        data = r.json()
        print("✅ Conexión exitosa con cookies.")
        print(f"📌 Issue: {data['key']} — {data['fields']['summary']}")
        assignee = data['fields']['assignee']['displayName'] if data['fields']['assignee'] else "Sin asignar"
        print(f"👤 Asignado a: {assignee}")
        return True
    elif r.status_code == 404:
        print("❌ El issue no existe o no tienes permisos para verlo.")
    elif r.status_code == 401:
        print("🔒 Sesión inválida o cookies expiradas. Vuelve a copiarlas desde Chrome.")
    else:
        print(f"⚠️ Error {r.status_code}: {r.text}")
    return False


if __name__ == "__main__":
    try:
        if probar_conexion_cookie():
            # Preguntar antes de ejecutar el otro script (opcional)
            respuesta = input("\n¿Deseas ejecutar el script de carga de horas? (s/n): ").strip().lower()
            if respuesta == "s":
                print("\n🚀 Ejecutando script de carga de horas...\n")
                subprocess.run(["python", "auto_worklog_semana_actual.py"])
            else:
                print("❎ Ejecución cancelada por el usuario.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")