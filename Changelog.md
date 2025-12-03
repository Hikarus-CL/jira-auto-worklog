# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1] - 2025-12-04
### Added
- Variables configurables para horas de trabajo:
  - `HORAS_DIARIAS_NORMAL`
  - `HORAS_DIARIAS_REDUCIDA`
- Variable configurable para comentarios:
  - `COMENTARIO`
- Actualización de `README.md` para reflejar nuevas variables.
- Actualización de `.env.example` con nuevos parámetros.

### Changed
- Comentario por defecto modificado a `"Actividad regular"`.

---

## [1.0] - 2025-12-04
### Added
- Autenticación mediante Cookie SSO.
- Validación de sesión y permisos en `main.py`.
- Detección de cookie expirada.
- Carga automática de horas para la semana completa.
- Detección de feriados de Chile.
- Prevención de duplicados.
- Estructura estándar del proyecto (`README`, `.env.example`, `requirements.txt`).
- Preparación para CLI en versión 2.0.

---