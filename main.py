import warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import requests
import json
from dotenv import load_dotenv
import os
import subprocess

# ============================================================
#  Cargar variables de entorno (.env)
# ============================================================
load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_ISSUE = os.getenv("JIRA_ISSUE")
JIRA_COOKIE = os.getenv("JIRA_COOKIE")

# Headers basados en cookies (SSO corporativo)
headers = {
    "Cookie": JIRA_COOKIE,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ============================================================
#  Validar cookie: probar acceso al issue
# ============================================================
def probar_cookie():
    """Verifica si la cookie funciona y retorna datos del issue."""
    url = f"{JIRA_URL}/rest/api/3/issue/{JIRA_ISSUE}"
    print(f"🔎 Probando acceso al issue: {url}")

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        data = r.json()
        print("✅ Conexión exitosa (cookie válida).")

        issue_key = data["key"]
        summary = data["fields"]["summary"]
        assignee = data["fields"]["assignee"]["displayName"] if data["fields"]["assignee"] else "Sin asignar"

        print(f"📌 Issue: {issue_key}")
        print(f"📝 Summary: {summary}")
        print(f"👤 Asignado a: {assignee}")

        return True

    elif r.status_code == 401:
        print("\n🔒 COOKIE EXPIRADA")
        print("La sesión SSO ya no es válida.")
        print("➡️ Copia nuevamente la cookie desde Chrome y reemplázala en tu archivo .env\n")
        return False

    elif r.status_code == 404:
        print("\n❌ El issue no existe o no tienes permisos para verlo.")
        return False

    else:
        print(f"\n⚠️ Error inesperado {r.status_code}: {r.text}")
        return False


# ============================================================
#  Ejecutar Script de carga semanal
# ============================================================
def ejecutar_script_semanal():
    print("\n🚀 Ejecutando carga de horas de la semana...\n")
    resultado = subprocess.run(["python", "auto_worklog_semana_actual.py"])
    if resultado.returncode == 0:
        print("\n✅ Carga semanal completada.")
    else:
        print("\n❌ Hubo un problema ejecutando el script semanal.")


# ============================================================
#  Flujo principal
# ============================================================
if __name__ == "__main__":
    try:
        if probar_cookie():
            # Solicitar confirmación antes de ejecutar
            respuesta = input("\n¿Deseas ejecutar el script de carga semanal? (s/n): ").strip().lower()
            if respuesta == "s":
                ejecutar_script_semanal()
            else:
                print("\n❎ Ejecución cancelada por el usuario.")
        else:
            print("⛔ No se puede continuar sin una cookie válida.")

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")