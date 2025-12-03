# Jira Auto Worklog ⏱️  
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Status](https://img.shields.io/badge/version-1.0-success)
![Auth](https://img.shields.io/badge/auth-SSO_Cookie-yellow)
![Platform](https://img.shields.io/badge/platform-Jira_Cloud-blue)

Automatizador de carga de horas en **Jira Cloud** usando **Python** y **autenticación por Cookie SSO**, ideal para cuentas corporativas donde **NO es posible usar API Tokens**.

Este proyecto registra worklogs automáticamente para la semana completa (lunes a viernes), evitando duplicados, detectando feriados y validando si la cookie está expirada.

---

# 🚀 Características

- Autenticación usando **Cookie SSO** (obligatoria para entornos corporativos).
- Carga automática de horas:
  - **Toda la semana actual (lunes a viernes)**.
- Detección automática de:
  - **Cookie expirada**
  - **Feriados de Chile**
  - **Worklogs ya existentes**
- Validación completa de permisos:
  - Acceso al issue
  - Summary
  - Asignatario
- Scripts claros y mensajes amigables.

---

# 📦 Instalación completa

Sigue estos pasos para instalar y ejecutar el proyecto por primera vez:

```bash
git clone https://github.com/Hikarus-CL/jira-auto-worklog.git
cd jira-auto-worklog

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Mac/Linux)
source venv/bin/activate

# En Windows (PowerShell)
# venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env
```

Luego edita `.env` con tus valores reales.

---

# 🔐 Variables de entorno

Debes crear tu archivo `.env` basándote en `.env.example`.

Ejemplo:

```
JIRA_URL=https://tudominio.atlassian.net
JIRA_ISSUE=PROY-123
JIRA_COOKIE=JSESSIONID=<jsessionid>; tenant.session.token=<jwt_token>;
```

---

# 📌 Cómo obtener la Cookie SSO (IMPORTANTE)

Tu empresa usa SSO, lo que significa que **NO puedes usar API Tokens**.  
Por lo tanto, necesitas copiar **dos cookies específicas** desde tu navegador:

### ✔ Las cookies necesarias son:
- `JSESSIONID`
- `tenant.session.token` (es un JWT muy largo)

### 📝 **Pasos para obtenerlas:**

1. Abre Jira en tu navegador e inicia sesión normalmente vía SSO.
2. Presiona **F12** para abrir las herramientas de desarrollador.
3. Ve a la pestaña **Application** (Chrome) o **Storage** (Firefox).
4. Selecciona la sección **Cookies** del dominio:
   ```
   https://tudominio.atlassian.net
   ```
5. Busca las cookies:
   - `JSESSIONID`
   - `tenant.session.token`
6. Copia sus valores **completos**.
7. Pégalos en tu `.env`, así:

```
JIRA_COOKIE=JSESSIONID=xxxxxxxx; tenant.session.token=yyyyyyyyy;
```

### ⚠️ Notas importantes:
- No uses comillas.
- Debe ir en **una sola línea**.
- Las cookies expiran, deberás actualizarlas cuando el script te indique cookie expirada.

---

# 🧠 Cómo funciona

## 🟣 1. `main.py` — Validación y ejecución semanal

Este script:

- Verifica si tu cookie es válida.
- Muestra el issue, summary, asignatario.
- Detecta cookie expirada.
- Pregunta si deseas ejecutar la carga semanal.
- Llama al script principal.

Ejemplo real:

```
🔎 Probando acceso al issue...
✅ Conexión exitosa (cookie válida)
📌 Issue: TBKCOS-25
📝 Summary: Consultoría CDC - Diciembre 2025
👤 Asignado a: Sin asignar
```

---

## 🟣 2. `auto_worklog_semana_actual.py` — Carga semanal de horas

Este script:

- Obtiene feriados desde Nager.Date.
- Obtiene tu `accountId`.
- Busca días ya registrados.
- Carga horas para lunes a viernes:
  - Lunes–jueves → **8.5 h**
  - Viernes → **6 h**

Ejemplo:

```
⚠️ Ya existía registro para 2025-12-01
⚠️ Ya existía registro para 2025-12-02
---------------------------------------------------
✅ Proceso completado. Días nuevos cargados: 0
📅 Rango procesado: 2025-12-01 → 2025-12-05
```

---

# ▶️ Ejecución

## Validar cookie + ejecutar semana completa

```bash
python main.py
```

## Ejecutar carga semanal directamente

```bash
python auto_worklog_semana_actual.py
```

*(El CLI se documentará en la versión 2.0)*

---

# 📂 Estructura del proyecto

```
jira-auto-worklog/
├── .gitignore
├── .env.example
├── main.py
├── auto_worklog_semana_actual.py
├── requirements.txt
└── README.md
```

---

# 🛠️ Mejoras futuras (Versión 2.0)

- CLI completo (check, daily, weekly)
- Logging a archivo (`.log`)
- Carga por rango de fechas
- Configuración avanzada via YAML
- Auto-renovación de cookies mediante navegador headless

---

# 👤 Autor

**Roberto Gómez Toro**  
Siebel CRM | Salesforce Developer | Python Automation  
GitHub: https://github.com/Hikarus-CL

---

# 📄 Licencia

Este proyecto no tiene licencia explícita.  
Todos los derechos reservados.