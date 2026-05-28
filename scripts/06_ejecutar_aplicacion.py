"""
GreenHouse Manager — Arranque de la Aplicación
===============================================
Orquesta el arranque completo del entorno local en el orden correcto:

  1. PostgreSQL (Docker o servicio local)
  2. Backend Spring Boot (mvn spring-boot:run)
  3. Frontend Vite (npm run dev)

Incluye:
  - Health check automático del backend (/actuator/health)
  - Detección del .env local para variables de entorno
  - Apertura del navegador al finalizar
  - Apagado limpio de todos los procesos al presionar Ctrl+C

Prerrequisitos:
  - Java 17+, Maven 3.9+, Node.js 20+, Docker (opcional)
  - Archivo .env configurado con credenciales de Google OAuth y Gmail

NOTA: Script DEMOSTRATIVO — no ejecutar directamente.
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
from pathlib import Path

ROOT     = Path(__file__).parent.parent
BACKEND  = ROOT / "greenhouse-backend"
FRONTEND = ROOT / "greenhouse-frontend"
ENV_FILE = ROOT / ".env"

BACKEND_URL  = "http://localhost:8080"
FRONTEND_URL = "http://localhost:5173"
HEALTH_URL   = f"{BACKEND_URL}/actuator/health"
SWAGGER_URL  = f"{BACKEND_URL}/swagger-ui.html"

# Tiempo máximo de espera para que el backend arranque (segundos)
BACKEND_TIMEOUT = 120


# ── Utilidades ─────────────────────────────────────────────────────────────────

def log(msg: str, emoji: str = "  "):
    print(f"{emoji} {msg}")


def cargar_env():
    """Carga variables del .env al entorno del proceso."""
    if not ENV_FILE.exists():
        log("⚠  Archivo .env no encontrado — usando valores por defecto")
        log("   Copia .env.example a .env y configura tus credenciales")
        return
    for linea in ENV_FILE.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            clave, _, valor = linea.partition("=")
            os.environ.setdefault(clave.strip(), valor.strip())
    log(".env cargado", "✓")


def verificar_prerrequisitos():
    """Verifica que Java, Maven y Node.js estén instalados."""
    checks = [
        (["java", "-version"],  "Java 17+"),
        (["mvn",  "--version"], "Maven 3.9+"),
        (["node", "--version"], "Node.js 20+"),
    ]
    todos_ok = True
    for cmd, nombre in checks:
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            log(f"{nombre} disponible", "  ✓")
        except (subprocess.CalledProcessError, FileNotFoundError):
            log(f"{nombre} NO encontrado — instálalo antes de continuar", "  ✗")
            todos_ok = False
    return todos_ok


def iniciar_postgresql():
    """
    Intenta iniciar PostgreSQL con Docker.
    Si Docker no está disponible, asume que PostgreSQL ya corre localmente.
    """
    log("Iniciando PostgreSQL...", "🐘")
    try:
        resultado = subprocess.run(
            ["docker", "compose", "up", "-d", "postgres"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if resultado.returncode == 0:
            log("PostgreSQL iniciado con Docker", "  ✓")
            time.sleep(3)  # Esperar a que la BD esté lista
            return True
        else:
            log("Docker no disponible — asumiendo PostgreSQL local en puerto 5432", "  ⚠")
            return True
    except FileNotFoundError:
        log("Docker no instalado — asumiendo PostgreSQL local en puerto 5432", "  ⚠")
        return True


def construir_variables_entorno() -> dict:
    """Construye el dict de variables de entorno para el backend."""
    env = os.environ.copy()
    env.update({
        "SPRING_DATASOURCE_URL":      os.getenv("DB_URL", "jdbc:postgresql://localhost:5432/greenhouse_db"),
        "SPRING_DATASOURCE_USERNAME": os.getenv("DB_USERNAME", "postgres"),
        "SPRING_DATASOURCE_PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "GOOGLE_CLIENT_ID":           os.getenv("GOOGLE_CLIENT_ID", "tu-client-id"),
        "GOOGLE_CLIENT_SECRET":       os.getenv("GOOGLE_CLIENT_SECRET", "tu-client-secret"),
        "MAIL_USERNAME":              os.getenv("MAIL_USERNAME", "tu-email@gmail.com"),
        "MAIL_PASSWORD":              os.getenv("MAIL_PASSWORD", "tu-app-password"),
        "BACKEND_URL":                BACKEND_URL,
        "FRONTEND_URL":               FRONTEND_URL,
    })
    return env


def iniciar_backend() -> subprocess.Popen:
    """Arranca el backend Spring Boot en background."""
    log("Iniciando backend Spring Boot...", "☕")
    env = construir_variables_entorno()

    proceso = subprocess.Popen(
        ["mvn", "spring-boot:run",
         "-Dspring-boot.run.profiles=local",
         f"-Dspring.datasource.url={env['SPRING_DATASOURCE_URL']}",
         f"-Dspring.datasource.username={env['SPRING_DATASOURCE_USERNAME']}",
         f"-Dspring.datasource.password={env['SPRING_DATASOURCE_PASSWORD']}",
         "-Dserver.servlet.session.cookie.secure=false",
         "-Dlogging.level.com.greenhouse=INFO",
        ],
        cwd=BACKEND,
        env=env,
    )
    return proceso


def esperar_backend(timeout: int = BACKEND_TIMEOUT) -> bool:
    """Hace health check hasta que el backend responda o se agote el tiempo."""
    import urllib.request
    log(f"Esperando backend (máx {timeout}s)...", "⏳")

    for i in range(timeout // 5):
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=3) as resp:
                if resp.status == 200:
                    log(f"Backend listo después de {(i+1)*5}s", "  ✓")
                    return True
        except Exception:
            pass
        time.sleep(5)
        print(f"     Intento {i+1}/{timeout//5}...", end="\r")

    log(f"Backend no respondió después de {timeout}s", "  ✗")
    return False


def iniciar_frontend() -> subprocess.Popen:
    """Instala dependencias si es necesario y arranca Vite en modo dev."""
    log("Iniciando frontend React + Vite...", "⚛️")

    node_modules = FRONTEND / "node_modules"
    if not node_modules.exists():
        log("Instalando dependencias npm...", "  📦")
        subprocess.run(["npm", "install"], cwd=FRONTEND, check=True)

    proceso = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND,
        env={**os.environ, "VITE_API_URL": f"{BACKEND_URL}/api"},
    )
    return proceso


def abrir_navegador():
    """Abre el navegador con la aplicación y Swagger."""
    time.sleep(3)
    log(f"Abriendo {FRONTEND_URL}", "🌐")
    webbrowser.open(FRONTEND_URL)
    time.sleep(1)
    log(f"Swagger UI: {SWAGGER_URL}", "📖")


def mostrar_info_inicio():
    """Muestra un resumen de lo que está corriendo."""
    print("\n" + "=" * 62)
    print("  ✅  GREENHOUSE MANAGER INICIADO CORRECTAMENTE")
    print("=" * 62)
    print(f"  🌐  Frontend:   {FRONTEND_URL}")
    print(f"  ☕  Backend:    {BACKEND_URL}")
    print(f"  📖  Swagger UI: {SWAGGER_URL}")
    print(f"  🐘  PostgreSQL: localhost:5432/greenhouse_db")
    print("=" * 62)
    print()
    print("  👥  Usuarios de prueba:")
    print("        admin@greenhouse.com    / Admin1234    (ADMINISTRADOR)")
    print("        supervisor@greenhouse.com / Super1234  (SUPERVISOR)")
    print("        juan@greenhouse.com     / Juan1234     (EMPLEADO)")
    print()
    print("  ⌨️   Presiona Ctrl+C para detener todos los procesos")
    print("=" * 62 + "\n")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "#" * 62)
    print("  GREENHOUSE MANAGER — ARRANQUE COMPLETO")
    print(f"  Raíz del proyecto: {ROOT}")
    print("#" * 62 + "\n")

    procesos = []

    def apagar(sig=None, frame=None):
        log("\nApagando todos los procesos...", "\n🛑")
        for p in procesos:
            try:
                p.terminate()
                p.wait(timeout=5)
                log(f"Proceso {p.pid} detenido", "  ✓")
            except Exception as e:
                log(f"Error deteniendo proceso {p.pid}: {e}", "  ⚠")
        log("Todos los procesos detenidos. ¡Hasta luego! 🌿", "\n✅")
        sys.exit(0)

    signal.signal(signal.SIGINT,  apagar)
    signal.signal(signal.SIGTERM, apagar)

    # ── 1. Cargar .env ─────────────────────────────────────────────────────────
    cargar_env()

    # ── 2. Verificar prerrequisitos ────────────────────────────────────────────
    log("Verificando prerrequisitos...", "🔍")
    if not verificar_prerrequisitos():
        log("Instala los prerrequisitos faltantes y vuelve a intentarlo.", "✗")
        sys.exit(1)

    # ── 3. PostgreSQL ──────────────────────────────────────────────────────────
    iniciar_postgresql()

    # ── 4. Backend ────────────────────────────────────────────────────────────
    proc_backend = iniciar_backend()
    procesos.append(proc_backend)

    if not esperar_backend():
        log("El backend no arrancó correctamente. Revisa los logs.", "✗")
        apagar()

    # ── 5. Frontend ───────────────────────────────────────────────────────────
    proc_frontend = iniciar_frontend()
    procesos.append(proc_frontend)
    time.sleep(3)

    # ── 6. Abrir navegador ────────────────────────────────────────────────────
    abrir_navegador()

    # ── 7. Mostrar info y mantener corriendo ──────────────────────────────────
    mostrar_info_inicio()

    # Mantener el script vivo hasta Ctrl+C
    while True:
        time.sleep(1)
        # Verificar que los procesos siguen corriendo
        for p in procesos:
            if p.poll() is not None:
                log(f"Proceso {p.pid} terminó inesperadamente (código {p.returncode})", "⚠️")


if __name__ == "__main__":
    main()
