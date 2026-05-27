#!/usr/bin/env python3
"""
GreenHouse Manager — Carga automática de historias de usuario en Taiga
======================================================================
Lee docs/user-stories.json y crea / actualiza todas las historias en Taiga.

Uso:
    python taiga-upload.py

Credenciales (desde .env o variables de entorno):
    TAIGA_URL             https://api.taiga.io/api/v1
    TAIGA_USERNAME        tu_usuario
    TAIGA_PASSWORD        tu_contraseña
    TAIGA_PROJECT_SLUG    cesar_camilo-greenhouse-manager
"""

import os
import json
import sys
import re
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Módulo 'requests' no encontrado. Ejecuta: pip install requests")
    sys.exit(1)

# ── Carga .env si existe ──────────────────────────────────────────────────────
ROOT = Path(__file__).parent
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

# ── Configuración ─────────────────────────────────────────────────────────────
TAIGA_URL  = os.getenv("TAIGA_URL",           "https://api.taiga.io/api/v1")
TAIGA_USER = os.getenv("TAIGA_USERNAME",      "cesar_camilo")
TAIGA_PASS = os.getenv("TAIGA_PASSWORD",      "")
TAIGA_SLUG = os.getenv("TAIGA_PROJECT_SLUG",  "cesar_camilo-greenhouse-manager")

USER_STORIES_FILE = ROOT / "docs" / "user-stories.json"

# ── Helpers de consola ────────────────────────────────────────────────────────
def ok(msg):   print(f"  ✅ {msg}")
def err(msg):  print(f"  ❌ {msg}")
def info(msg): print(f"  ℹ️  {msg}")
def title(msg): print(f"\n{'─'*60}\n  {msg}\n{'─'*60}")

# ── Taiga API ─────────────────────────────────────────────────────────────────
session = requests.Session()

def taiga_login():
    """Autenticación en Taiga, devuelve token."""
    password = TAIGA_PASS
    if not password:
        import getpass
        password = getpass.getpass(f"  Contraseña para '{TAIGA_USER}' en Taiga: ")

    resp = session.post(f"{TAIGA_URL}/auth", json={
        "type": "normal",
        "username": TAIGA_USER,
        "password": password,
    }, timeout=15)

    if resp.status_code != 200:
        err(f"Login fallido: {resp.status_code} — {resp.text[:200]}")
        sys.exit(1)

    token = resp.json()["auth_token"]
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    })
    ok(f"Autenticado como '{TAIGA_USER}'")
    return token


def get_project():
    """Obtiene el proyecto por slug."""
    resp = session.get(f"{TAIGA_URL}/projects/by_slug?slug={TAIGA_SLUG}", timeout=10)
    if resp.status_code != 200:
        err(f"Proyecto '{TAIGA_SLUG}' no encontrado: {resp.status_code}")
        err("Verifica que el proyecto exista en taiga.io y que el slug sea correcto.")
        sys.exit(1)

    project = resp.json()
    ok(f"Proyecto encontrado: '{project['name']}' (id={project['id']})")
    return project


def get_existing_stories(project_id):
    """Devuelve dict {subject_lower: story} de las historias existentes."""
    resp = session.get(f"{TAIGA_URL}/userstories?project={project_id}", timeout=15)
    if resp.status_code != 200:
        return {}
    return {s["subject"].lower(): s for s in resp.json()}


def get_or_create_milestone(project_id, sprint_num, sprint_name):
    """Obtiene o crea un milestone (sprint) en Taiga."""
    # Listar milestones existentes
    resp = session.get(f"{TAIGA_URL}/milestones?project={project_id}", timeout=10)
    if resp.status_code == 200:
        for m in resp.json():
            if (f"sprint {sprint_num}" in m["name"].lower() or
                    sprint_name.lower() in m["name"].lower()):
                info(f"  Sprint existente: '{m['name']}'")
                return m["id"]

    # Crear milestone
    from datetime import date, timedelta
    start = date.today() + timedelta(weeks=(sprint_num - 1) * 2)
    end   = start + timedelta(weeks=2)

    payload = {
        "project":        project_id,
        "name":           f"Sprint {sprint_num}: {sprint_name}",
        "estimated_start": str(start),
        "estimated_finish": str(end),
    }
    resp = session.post(f"{TAIGA_URL}/milestones", json=payload, timeout=10)
    if resp.status_code in [200, 201]:
        ok(f"  Sprint creado: 'Sprint {sprint_num}: {sprint_name}'")
        return resp.json()["id"]
    else:
        err(f"  No se pudo crear el sprint: {resp.status_code} — {resp.text[:150]}")
        return None


def build_description(story):
    """Construye la descripción enriquecida con criterios de aceptación."""
    desc = story.get("description", "")
    criteria = story.get("acceptance_criteria", [])
    ref  = story.get("ref", "")

    if criteria:
        desc += f"\n\n**Criterios de aceptación ({ref}):**\n"
        for c in criteria:
            desc += f"- {c}\n"

    return desc


def create_or_update_story(project_id, milestone_id, story, existing):
    """Crea una historia de usuario o la actualiza si ya existe."""
    subject      = story["subject"]
    subject_low  = subject.lower()

    # Buscar coincidencia aproximada
    existing_match = None
    for key, val in existing.items():
        if subject_low == key or subject_low in key or key in subject_low:
            existing_match = val
            break

    tags        = story.get("tags", [])
    points      = story.get("points", 0)
    description = build_description(story)
    ref         = story.get("ref", "")

    payload = {
        "project":     project_id,
        "subject":     subject,
        "description": description,
        "tags":        tags,
        "milestone":   milestone_id,
    }

    if existing_match:
        # Actualizar
        story_id = existing_match["id"]
        version  = existing_match.get("version", 1)
        payload["version"] = version
        resp = session.patch(
            f"{TAIGA_URL}/userstories/{story_id}",
            json=payload, timeout=10
        )
        if resp.status_code in [200, 204]:
            ok(f"    [{ref}] Actualizada: {subject[:55]}")
            return resp.json() if resp.content else existing_match
        else:
            err(f"    [{ref}] Error al actualizar: {resp.status_code} — {resp.text[:100]}")
            return None
    else:
        # Crear nueva
        resp = session.post(f"{TAIGA_URL}/userstories", json=payload, timeout=10)
        if resp.status_code in [200, 201]:
            ok(f"    [{ref}] Creada:      {subject[:55]}")
            return resp.json()
        else:
            err(f"    [{ref}] Error al crear: {resp.status_code} — {resp.text[:100]}")
            return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print()
    print("  🌿  GreenHouse Manager — Taiga Upload")
    print("  " + "═" * 40)
    print(f"  Proyecto : {TAIGA_SLUG}")
    print(f"  API      : {TAIGA_URL}")
    print()

    # 1. Verificar archivo de historias
    if not USER_STORIES_FILE.exists():
        err(f"No se encontró el archivo: {USER_STORIES_FILE}")
        sys.exit(1)

    with open(USER_STORIES_FILE, encoding="utf-8") as f:
        data = json.load(f)

    sprints = data.get("sprints", [])
    total_stories = sum(len(s["stories"]) for s in sprints)
    info(f"Historias encontradas en docs/user-stories.json: {total_stories}")
    print()

    # 2. Login
    title("1 / 4  Autenticando en Taiga")
    taiga_login()

    # 3. Obtener proyecto
    title("2 / 4  Verificando proyecto")
    project = get_project()
    project_id = project["id"]

    # 4. Cargar historias existentes
    title("3 / 4  Cargando historias actuales de Taiga")
    existing = get_existing_stories(project_id)
    info(f"Historias ya en Taiga: {len(existing)}")

    # 5. Crear / actualizar por sprint
    title("4 / 4  Sincronizando historias")
    created = 0
    updated = 0
    failed  = 0

    for sprint_data in sprints:
        sprint_num  = sprint_data["sprint"]
        sprint_name = sprint_data["name"]
        stories     = sprint_data["stories"]

        print(f"\n  📦 Sprint {sprint_num}: {sprint_name} ({len(stories)} historias)")

        milestone_id = get_or_create_milestone(project_id, sprint_num, sprint_name)

        for story in stories:
            subject_low = story["subject"].lower()
            was_existing = any(
                subject_low == k or subject_low in k or k in subject_low
                for k in existing
            )

            result = create_or_update_story(project_id, milestone_id, story, existing)
            if result:
                if was_existing:
                    updated += 1
                else:
                    created += 1
                    # Agregar a existentes para detectar duplicados dentro del mismo run
                    existing[story["subject"].lower()] = result
            else:
                failed += 1

    # ── Resumen final ─────────────────────────────────────────────────────────
    print()
    print("  " + "═" * 50)
    print("  🌿  Taiga Upload — Completado")
    print("  " + "═" * 50)
    print(f"  ✅ Creadas  : {created}")
    print(f"  🔄 Actualizadas: {updated}")
    if failed:
        print(f"  ❌ Fallidas : {failed}")
    print(f"\n  🔗 Ver en: https://tree.taiga.io/project/{TAIGA_SLUG}/backlog")
    print()


if __name__ == "__main__":
    main()
