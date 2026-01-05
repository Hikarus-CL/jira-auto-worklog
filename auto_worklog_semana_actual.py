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
            print(f"⚠️  No se pudo obtener feriados ({r.status_code}). Usando lista vacía.")
            return set()

        datos = r.json()
        feriados = { item["date"] for item in datos }
        print(f"📅 Feriados {year} cargados ")
        # print(f"{sorted(feriados)}")
        return feriados

    except Exception as e:
        print(f"⚠️  Error consultando API de feriados: {e}")
        return set()

# Cargar variables del archivo .env
load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_COOKIE = os.getenv("JIRA_COOKIE")
JIRA_ISSUE = os.getenv("JIRA_ISSUE")
JIRA_ISSUE_MAP_JSON = os.getenv("JIRA_ISSUE_MAP_JSON", "")

headers = {
    "Cookie": JIRA_COOKIE,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

HORAS_DIARIAS_NORMAL = float(os.getenv("HORAS_DIARIAS_NORMAL", 8.5))
HORAS_DIARIAS_REDUCIDA = float(os.getenv("HORAS_DIARIAS_REDUCIDA", 6))
COMENTARIO = os.getenv("COMENTARIO", "Actividad regular")


def _parse_issue_map():
    """Parsea el JSON del mapping por mes (YYYY-MM -> ISSUEKEY)."""
    if not JIRA_ISSUE_MAP_JSON:
        return {}
    try:
        data = json.loads(JIRA_ISSUE_MAP_JSON)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def get_issue_for_date(d: datetime):
    """Retorna issue por mes (YYYY-MM) o por año (YYYY). Fallback a JIRA_ISSUE."""
    issue_map = _parse_issue_map()

    key_month = f"{d.year:04d}-{d.month:02d}"  # prioridad: mapping mensual
    key_year = f"{d.year:04d}"                 # fallback: mapping anual

    return issue_map.get(key_month) or issue_map.get(key_year) or JIRA_ISSUE


def obtener_account_id():
    """Obtiene el accountId del usuario autenticado."""
    r = requests.get(f"{JIRA_URL}/rest/api/3/myself", headers=headers)
    if r.status_code != 200:
        print(f"⚠️  No se pudo obtener el usuario actual ({r.status_code}): {r.text}")
        return None
    data = r.json()
    return data.get("accountId"), data.get("displayName")


def obtener_worklogs_existentes(mi_account_id, issue_key):
    """Devuelve las fechas con worklogs ya registrados (YYYY-MM-DD) solo del usuario actual, para un issue."""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/worklog"
    r = requests.get(url, headers=headers)
    if r.status_code == 401:
        print("🔒 Sesión expirada. Vuelve a copiar la cookie desde Chrome.")
        return set()
    elif r.status_code != 200:
        print(f"⚠️  No se pudo consultar worklogs del issue {issue_key} ({r.status_code}): {r.text}")
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
    lunes = hoy - timedelta(days=hoy.weekday())  # lunes de esta semana
    viernes = lunes + timedelta(days=4)

    # Cargar feriados para todos los años presentes en el rango (importante en fin de año)
    years = sorted({(lunes + timedelta(days=i)).year for i in range(5)})
    feriados = set()
    for y in years:
        feriados |= obtener_feriados(y)

    print(f"\n👤 Usuario: {nombre}")
    print(f"📅 Semana actual: {lunes.strftime('%Y-%m-%d')} → {viernes.strftime('%Y-%m-%d')}")
    print("---------------------------------------------------")

    dias_cargados = 0

    # Armar lista de días (lunes a viernes)
    dias_semana = [lunes + timedelta(days=i) for i in range(5)]

    # Agrupar por issue según el mes de cada día
    dias_por_issue = {}
    for fecha in dias_semana:
        # Omite fines de semana por seguridad
        if fecha.weekday() >= 5:
            continue

        issue_key = get_issue_for_date(fecha)
        if not issue_key:
            print(f"⛔ No hay issue configurado para {fecha.strftime('%Y-%m-%d')} (define JIRA_ISSUE o JIRA_ISSUE_MAP_JSON)")
            continue

        dias_por_issue.setdefault(issue_key, []).append(fecha)

    # Procesar por issue: consultar existentes una sola vez y luego postear los faltantes
    for issue_key, dias in dias_por_issue.items():
        existentes = obtener_worklogs_existentes(mi_account_id, issue_key)
        print(f"\n📌 Issue {issue_key}: {len(dias)} día(s) a evaluar")

        for fecha in dias:
            fecha_str = fecha.strftime("%Y-%m-%d")

            if fecha_str in feriados:
                print(f"🎉 {fecha_str} es feriado según la API. No se registran horas.")
                continue

            # Omite días ya registrados
            if fecha_str in existentes:
                print(f"⚠️  {fecha_str} Ya existía registro de horas para ese día en {issue_key}")
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

            print(f"📤 Enviando payload para {fecha_str} en {issue_key}:")
            # print(json.dumps(payload, indent=2), "\n")

            url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/worklog"
            r = requests.post(url, headers=headers, data=json.dumps(payload))

            if r.status_code == 201:
                dias_cargados += 1
                existentes.add(fecha_str)  # para evitar duplicar en la misma corrida
                print(f"✅ {fecha_str}: {horas}h registradas correctamente en {issue_key}")
            else:
                print(f"⚠️  Error {r.status_code} en {fecha_str} ({issue_key}): {r.text}")

    print("---------------------------------------------------")
    print(f"✅ Proceso completado. Días nuevos cargados: {dias_cargados}")
    print(f"📅 Rango procesado: {lunes.strftime('%Y-%m-%d')} → {viernes.strftime('%Y-%m-%d')}")


if __name__ == "__main__":
    registrar_horas()