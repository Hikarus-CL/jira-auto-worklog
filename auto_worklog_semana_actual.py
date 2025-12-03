import warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def obtener_feriados(year):
    """Obtiene feriados de Chile desde la API Nager.Date."""
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/CL"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ No se pudo obtener feriados ({r.status_code}). Usando lista vacía.")
            return set()

        datos = r.json()
        feriados = { item["date"] for item in datos }
        print(f"📅 Feriados cargados: {sorted(feriados)}")
        return feriados

    except Exception as e:
        print(f"⚠️ Error consultando API de feriados: {e}")
        return set()

# Cargar variables del archivo .env
load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_COOKIE = os.getenv("JIRA_COOKIE")
JIRA_ISSUE = os.getenv("JIRA_ISSUE")

headers = {
    "Cookie": JIRA_COOKIE,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

HORAS_DIARIAS_NORMAL = float(os.getenv("HORAS_DIARIAS_NORMAL", 8.5))
HORAS_DIARIAS_REDUCIDA = float(os.getenv("HORAS_DIARIAS_REDUCIDA", 6))
COMENTARIO = os.getenv("COMENTARIO", "Actividad regular")


def obtener_account_id():
    """Obtiene el accountId del usuario autenticado."""
    r = requests.get(f"{JIRA_URL}/rest/api/3/myself", headers=headers)
    if r.status_code != 200:
        print(f"⚠️ No se pudo obtener el usuario actual ({r.status_code}): {r.text}")
        return None
    data = r.json()
    return data.get("accountId"), data.get("displayName")


def obtener_worklogs_existentes(mi_account_id):
    """Devuelve las fechas con worklogs ya registrados (YYYY-MM-DD) solo del usuario actual."""
    url = f"{JIRA_URL}/rest/api/3/issue/{JIRA_ISSUE}/worklog"
    r = requests.get(url, headers=headers)
    if r.status_code == 401:
        print("🔒 Sesión expirada. Vuelve a copiar la cookie desde Chrome.")
        return set()
    elif r.status_code != 200:
        print(f"⚠️ No se pudo consultar worklogs ({r.status_code}): {r.text}")
        return set()

    data = r.json()
    fechas = {
        wl["started"][:10]
        for wl in data.get("worklogs", [])
        if wl.get("author", {}).get("accountId") == mi_account_id
    }
    return fechas


def registrar_horas():
    """Registra horas desde el lunes hasta el viernes de la semana actual, omitiendo las ya cargadas."""
    mi_account_id, nombre = obtener_account_id()
    if not mi_account_id:
        print("❌ No se pudo obtener el accountId del usuario actual.")
        return

    hoy = datetime.now()
    year = hoy.year
    feriados = obtener_feriados(year)
    lunes = hoy - timedelta(days=hoy.weekday())  # lunes de esta semana
    viernes = lunes + timedelta(days=4)
    existentes = obtener_worklogs_existentes(mi_account_id)

    print(f"\n👤 Usuario: {nombre}")
    print(f"📅 Semana actual: {lunes.strftime('%Y-%m-%d')} → {viernes.strftime('%Y-%m-%d')}")
    print("---------------------------------------------------")

    dias_cargados = 0

    for i in range(5):
        fecha = lunes + timedelta(days=i)
        fecha_str = fecha.strftime("%Y-%m-%d")

        # Omite fines de semana por seguridad
        if fecha.weekday() >= 5:
            continue

        if fecha_str in feriados:
            print(f"🎉 {fecha_str} es feriado según la API. No se registran horas.")
            continue

        # Omite días ya registrados
        if fecha_str in existentes:
            print(f"⚠️ Ya existía registro para {fecha_str}")
            continue

        horas = HORAS_DIARIAS_REDUCIDA if fecha.weekday() == 4 else HORAS_DIARIAS_NORMAL
        minutos = int(horas * 60)

        # Payload en formato real del UI de Jira
        payload = {
            "timeSpent": f"{minutos}m",
            "started": fecha.strftime("%Y-%m-%dT09:00:00.000-0300"),
            "comment": {
                "version": 1,
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": COMENTARIO}
                        ]
                    }
                ]
            }
        }

        print(f"📤 Enviando payload para {fecha_str}:\n{json.dumps(payload, indent=2)}\n")

        url = f"{JIRA_URL}/rest/api/3/issue/{JIRA_ISSUE}/worklog"
        r = requests.post(url, headers=headers, data=json.dumps(payload))

        if r.status_code == 201:
            dias_cargados += 1
            print(f"✅ {fecha_str}: {horas}h registradas correctamente")
        else:
            print(f"⚠️ Error {r.status_code} en {fecha_str}: {r.text}")

    print("---------------------------------------------------")
    print(f"✅ Proceso completado. Días nuevos cargados: {dias_cargados}")
    print(f"📅 Rango procesado: {lunes.strftime('%Y-%m-%d')} → {viernes.strftime('%Y-%m-%d')}")


if __name__ == "__main__":
    registrar_horas()