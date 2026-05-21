\*# GreenHouse Manager — Configuración de Taiga

**Autores:** Cesar Hoyos - Julian Delgado  
**Fecha:** 2026  
**Asignatura:** Electiva de Ingeniería de Software

---

## ¿Qué es Taiga y por qué lo usamos?

[Taiga](https://taiga.io) es una plataforma de gestión ágil de proyectos. En este proyecto se usa para:

- Registrar las **historias de usuario** del sistema
- Definir los **criterios de aceptación** de cada historia
- Conectar las pruebas automatizadas con las historias (`test_taiga_integration.py`)
- Cumplir el punto 9 de la rúbrica: _"Conectividad de Taiga para la validación de historias de usuario"_

---

## Paso 1 — Crear cuenta y proyecto en Taiga

1. Ir a [https://taiga.io](https://taiga.io) → **Sign up** (gratuito)
2. Crear nuevo proyecto:
   - Nombre: `GreenHouse Manager`
   - Slug: `greenhouse-manager`
   - Tipo: **Scrum**
   - Privacidad: Pública (para que el CI/CD pueda acceder)

---

## Paso 2 — Crear las Historias de Usuario

En el panel de Taiga, crear las siguientes historias en el **Backlog**:

| #     | Historia de Usuario                            | Criterios de Aceptación                                                                                                                                                        |
| ----- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| HU-01 | Inicio de sesión con email y contraseña        | CA1: Login exitoso redirige al dashboard. CA2: Credenciales incorrectas muestran mensaje de error. CA3: Correo no verificado muestra aviso específico.                         |
| HU-02 | Inicio de sesión con Google OAuth              | CA1: El botón de Google es visible en la pantalla de login. CA2: El flujo OAuth completa el registro automático si es nuevo usuario. CA3: Error de OAuth redirige con mensaje. |
| HU-03 | Registro de usuario con verificación de correo | CA1: El formulario valida campos requeridos. CA2: Se envía correo de verificación al registrarse. CA3: El enlace de verificación expira en 24h.                                |
| HU-04 | Visualizar panel de control con estadísticas   | CA1: Muestra conteo de plantas activas. CA2: Muestra alertas pendientes. CA3: Muestra kg cosechados del mes. CA4: Muestra zonas activas.                                       |
| HU-05 | Gestión de zonas del invernadero               | CA1: Se pueden listar todas las zonas. CA2: Se puede crear una zona con nombre único. CA3: Se puede cambiar el estado de una zona.                                             |
| HU-06 | Gestión de plantas por ciclo de vida           | CA1: Se listan plantas con su estado actual. CA2: El estado cambia a través del ciclo: SEMBRADA → COSECHADA. CA3: Se puede filtrar por zona o estado.                          |
| HU-07 | Monitoreo de alertas generadas por sensores    | CA1: Las alertas se generan automáticamente al superar umbrales. CA2: La severidad se calcula según % de desviación. CA3: El usuario puede marcar alertas como atendidas.      |
| HU-08 | Registro de cosechas con calidad y destino     | CA1: Se registra peso, calidad (A/B/C) y destino. CA2: Las estadísticas del mes se calculan automáticamente. CA3: Se asocia la cosecha al empleado responsable.                |
| HU-09 | Gestión de empleados y roles                   | CA1: Solo ADMINISTRADOR puede crear/eliminar empleados. CA2: Los roles determinan el acceso a las secciones. CA3: Empleados inactivos no pueden iniciar sesión.                |
| HU-10 | Internacionalización del sistema               | CA1: La interfaz está disponible en español e inglés. CA2: El idioma se cambia sin recargar la página. CA3: Los mensajes de error del backend están en español.                |

---

## Paso 3 — Obtener credenciales de API

En Taiga, las credenciales para la API son las mismas del usuario:

```
TAIGA_URL      = https://api.taiga.io/api/v1
TAIGA_USERNAME = tu-usuario-en-taiga
TAIGA_PASSWORD = tu-contraseña-en-taiga
TAIGA_PROJECT_SLUG = greenhouse-manager
```

---

## Paso 4 — Configurar variables en GitHub Actions

En el repositorio de GitHub:

1. Ir a **Settings → Secrets and variables → Actions**
2. Agregar los siguientes **Repository Secrets**:

| Secret               | Valor                         |
| -------------------- | ----------------------------- |
| `TAIGA_URL`          | `https://api.taiga.io/api/v1` |
| `TAIGA_USERNAME`     | tu usuario de Taiga           |
| `TAIGA_PASSWORD`     | tu contraseña de Taiga        |
| `TAIGA_PROJECT_SLUG` | `greenhouse-manager`          |

---

## Paso 5 — Ejecutar pruebas de integración con Taiga localmente

```powershell
cd tests-python

# Configurar variables de entorno
$env:TAIGA_URL      = "https://api.taiga.io/api/v1"
$env:TAIGA_USERNAME = "tu-usuario"
$env:TAIGA_PASSWORD = "tu-contraseña"
$env:TAIGA_PROJECT_SLUG = "greenhouse-manager"
$env:API_BASE_URL   = "http://localhost:8080"

# Ejecutar solo los tests de Taiga
pytest test_taiga_integration.py -v
```

---

## Estructura de `test_taiga_integration.py`

El archivo contiene dos clases de prueba:

### `TestTaigaConectividad`

Verifica que el proyecto existe en Taiga y tiene las historias correctas:

- `test_taiga_api_accessible` — La API de Taiga responde
- `test_project_exists_in_taiga` — El proyecto `greenhouse-manager` existe
- `test_project_has_user_stories` — Tiene al menos 5 historias de usuario
- `test_required_user_stories_exist` — Al menos el 70% de las HU requeridas están presentes

### `TestCriteriosAceptacion`

Valida cada criterio de aceptación haciendo llamadas reales a la API del sistema:

- `test_ca_login_endpoint_exists` — El endpoint de autenticación responde
- `test_ca_zonas_crud_available` — El CRUD de zonas funciona (HU-05)
- `test_ca_plantas_list_available` — El listado de plantas funciona (HU-06)
- `test_ca_alertas_count_endpoint` — El conteo de alertas funciona (HU-07)
- `test_ca_cosechas_estadisticas_endpoint` — Las estadísticas de cosechas funcionan (HU-08)
- `test_ca_empleados_requires_auth` — Los empleados requieren autenticación (HU-09)
- `test_ca_oauth2_endpoint_available` — El endpoint OAuth2 está disponible (HU-02)
- `test_ca_swagger_documentation_available` — Swagger UI está disponible

---

## Resultado esperado

```
tests-python/test_taiga_integration.py::TestTaigaConectividad::test_taiga_api_accessible        PASSED
tests-python/test_taiga_integration.py::TestTaigaConectividad::test_project_exists_in_taiga     PASSED
tests-python/test_taiga_integration.py::TestTaigaConectividad::test_project_has_user_stories    PASSED
tests-python/test_taiga_integration.py::TestTaigaConectividad::test_required_user_stories_exist PASSED
tests-python/test_taiga_integration.py::TestCriteriosAceptacion::test_ca_login_endpoint_exists  PASSED
...
8 passed in 5.23s
```
