# GreenHouse Manager — Tests de Selenium (Frontend)

**Autores:** [Nombres del equipo] | **Fecha:** 2026

Suite de pruebas de interfaz de usuario automatizadas con **Selenium WebDriver** y **pytest**.

---

## Requisitos previos

- Python 3.10+
- Google Chrome instalado
- Backend corriendo en `http://localhost:8080`
- Frontend corriendo en `http://localhost:5173`
- Datos de prueba cargados (admin@greenhouse.com / Admin1234)

---

## Instalación

```powershell
cd tests-selenium
pip install -r requirements.txt
```

---

## Ejecución

```powershell
# Todos los tests (genera reporte HTML)
pytest

# Solo tests de autenticación
pytest test_auth.py -v

# Solo tests del dashboard
pytest test_dashboard.py -v

# Ver el reporte generado
start reporte-selenium.html
```

---

## Tests incluidos

| Archivo | Historias de Usuario | Descripción |
|---------|:---:|-------------|
| `test_auth.py` | HU-01 a HU-05 | Login, registro, toggle contraseña, OAuth |
| `test_dashboard.py` | HU-06 a HU-09 | Panel de control, estadísticas, navegación |
| `test_zonas_ui.py` | HU-10 a HU-12 | Listado y estados de zonas |
| `test_plantas_ui.py` | HU-13 a HU-15 | Listado de plantas y estados |
| `test_alertas_ui.py` | HU-16 a HU-18 | Alertas, severidades y estados |
| `test_cosechas_ui.py` | HU-19 a HU-21 | Cosechas y calidades |

**Total: 25 casos de prueba de interfaz**

---

## Notas

- Los tests corren en **modo headless** (sin ventana visible) para compatibilidad con CI/CD
- El fixture `authenticated_driver` realiza login una sola vez y reutiliza la sesión
- `webdriver-manager` descarga automáticamente el ChromeDriver compatible con tu versión de Chrome
