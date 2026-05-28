"""
GreenHouse Manager — Generador del Frontend React + Vite
=========================================================
Lee docs/modelo-json.json y genera la estructura completa del frontend:

  greenhouse-frontend/
  ├── package.json            (React 18, Vite, TailwindCSS, react-query, axios, i18next)
  ├── vite.config.ts
  ├── tsconfig.json
  ├── tailwind.config.js
  ├── index.html
  ├── Dockerfile
  ├── nginx.conf
  └── src/
      ├── main.tsx
      ├── App.tsx             (rutas protegidas con PrivateRoute)
      ├── types.ts            (interfaces TypeScript por entidad)
      ├── services/
      │   └── api.ts          (axios + servicios CRUD por entidad)
      ├── context/
      │   └── AuthContext.tsx  (isAdmin, canWrite, user)
      ├── components/
      │   ├── PrivateRoute.tsx
      │   └── layout/
      │       └── Layout.tsx   (sidebar verde, nav items por rol)
      ├── pages/
      │   ├── LoginPage.tsx
      │   ├── RegisterPage.tsx
      │   ├── DashboardPage.tsx
      │   ├── ZonasPage.tsx    (CRUD + sensores inline)
      │   ├── PlantasPage.tsx
      │   ├── SensoresPage.tsx
      │   ├── AlertasPage.tsx  (atender/descartar + alertas manuales)
      │   ├── CosechasPage.tsx
      │   ├── EmpleadosPage.tsx
      │   ├── NovedadesPage.tsx
      │   └── TaigaPage.tsx   (solo ADMIN — historias agrupadas por sprint)
      └── i18n/
          └── index.ts         (español e inglés completo)

NOTA: Script DEMOSTRATIVO — no ejecutar directamente.
"""

import json
from pathlib import Path
from datetime import date

ROOT      = Path(__file__).parent.parent
MODELO    = ROOT / "docs" / "modelo-json.json"
FRONTEND  = ROOT / "greenhouse-frontend"
SRC       = FRONTEND / "src"

HEADER_TS = f"""\
/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: {date.today().year}
 * Generado automáticamente desde docs/modelo-json.json
 */
"""


def escribir(path: Path, contenido: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contenido, encoding="utf-8")
    print(f"  [FRONTEND] Creado: {path.relative_to(ROOT)}")


# ── package.json ───────────────────────────────────────────────────────────────

def generar_package_json():
    contenido = json.dumps({
        "name": "greenhouse-frontend",
        "version": "1.0.0",
        "description": "GreenHouse Manager - Frontend React",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "tsc && vite build",
            "preview": "vite preview",
            "test": "vitest"
        },
        "dependencies": {
            "serve": "^14.2.3",
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "react-router-dom": "^6.24.0",
            "axios": "^1.7.2",
            "i18next": "^23.11.5",
            "react-i18next": "^14.1.2",
            "recharts": "^2.12.7",
            "@tanstack/react-query": "^5.45.1",
            "react-hot-toast": "^2.4.1",
            "lucide-react": "^0.400.0"
        },
        "devDependencies": {
            "@types/react": "^18.3.3",
            "@types/react-dom": "^18.3.0",
            "@vitejs/plugin-react": "^4.3.1",
            "typescript": "^5.5.3",
            "vite": "^5.3.4",
            "vitest": "^1.6.0",
            "autoprefixer": "^10.4.19",
            "postcss": "^8.4.39",
            "tailwindcss": "^3.4.6"
        }
    }, indent=2)
    escribir(FRONTEND / "package.json", contenido)


# ── vite.config.ts ─────────────────────────────────────────────────────────────

def generar_vite_config():
    contenido = f"""{HEADER_TS}
import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({{
  plugins: [react()],
  server: {{
    proxy: {{
      '/api': {{
        target: 'http://localhost:8080',
        changeOrigin: true,
      }},
      '/oauth2': {{
        target: 'http://localhost:8080',
        changeOrigin: true,
      }},
      '/login': {{
        target: 'http://localhost:8080',
        changeOrigin: true,
      }},
    }},
  }},
}})
"""
    escribir(FRONTEND / "vite.config.ts", contenido)


# ── types.ts ───────────────────────────────────────────────────────────────────

def generar_types(modelo: dict):
    """Genera interfaces TypeScript desde las entidades del modelo."""
    entidades = modelo.get("entities", {})

    tipo_map = {
        "integer": "number",
        "number":  "number",
        "boolean": "boolean",
        "string":  "string",
    }

    interfaces = []
    for nombre, entidad in entidades.items():
        props = entidad.get("properties", {})
        campos = []
        for pname, pdef in props.items():
            if "$ref" in pdef:
                ref_clase = pdef["$ref"].replace("#/entities/", "")
                nullable  = pdef.get("nullable", False)
                opt = "?" if nullable else ""
                campos.append(f"  {pname}{opt}: {ref_clase} | null")
            else:
                enums = pdef.get("enum", [])
                if enums:
                    ts_type = " | ".join(f"'{e}'" for e in enums)
                else:
                    ts_type = tipo_map.get(pdef.get("type", "string"), "string")
                opt = "?" if pname == "id" or pname == "observaciones" else ""
                campos.append(f"  {pname}{opt}: {ts_type}")

        campos_str = "\n".join(campos)
        desc = entidad.get("description", "")
        interfaces.append(f"/** {desc} */\nexport interface {nombre} {{\n{campos_str}\n}}")

    contenido = f"""{HEADER_TS}
// ── Interfaces TypeScript generadas desde docs/modelo-json.json ──────────────

{"\\n\\n".join(interfaces)}
"""
    escribir(SRC / "types.ts", contenido)


# ── services/api.ts ────────────────────────────────────────────────────────────

def generar_api_service(modelo: dict):
    entidades = modelo.get("entities", {})

    servicios = []
    for nombre, entidad in entidades.items():
        tabla    = entidad.get("table", nombre.lower())
        url_path = tabla.replace("_", "-") + "s"
        var_name = nombre[0].lower() + nombre[1:] + "Service"
        desc     = entidad.get("description", "")

        servicio = f"""\
/**
 * Servicio para operaciones CRUD sobre {nombre}.
 * <p>{desc}</p>
 * Endpoints: GET/POST/PUT/DELETE /api/{url_path}
 */
export const {var_name} = {{
  /** Retorna todos los registros. */
  getAll:    ()              => api.get('/{url_path}'),
  /** Retorna un registro por su ID. */
  getById:   (id: number)   => api.get(`/{url_path}/${{id}}`),
  /** Crea un nuevo registro. */
  create:    (data: object) => api.post('/{url_path}', data),
  /** Actualiza un registro existente. */
  update:    (id: number, data: object) => api.put(`/{url_path}/${{id}}`, data),
  /** Elimina un registro. */
  delete:    (id: number)   => api.delete(`/{url_path}/${{id}}`),
}}"""
        servicios.append(servicio)

    contenido = f"""{HEADER_TS}
import axios from 'axios'

/**
 * Instancia base de Axios configurada para GreenHouse Manager.
 * En desarrollo usa el proxy de Vite (/api → localhost:8080).
 * En producción Railway usa VITE_API_URL.
 */
const api = axios.create({{
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
  withCredentials: true,
  headers: {{ 'Content-Type': 'application/json' }},
}})

/** Interceptor: redirige a /login cuando el backend responde 401. */
api.interceptors.response.use(
  res => res,
  err => {{
    const publicPaths = ['/login', '/register']
    const onPublicPage = publicPaths.some(p => window.location.pathname.startsWith(p))
    if (err.response?.status === 401 && !onPublicPage) {{
      window.location.href = '/login'
    }}
    return Promise.reject(err)
  }}
)

{"\\n\\n".join(servicios)}

/**
 * Servicio proxy para historias de usuario de Taiga.
 * Solo accesible para usuarios con rol ADMINISTRADOR.
 */
export const taigaService = {{
  /** Retorna todas las historias del proyecto Taiga, agrupables por sprint. */
  getHistorias: () => api.get('/taiga/historias'),
}}

export default api
"""
    escribir(SRC / "services" / "api.ts", contenido)


# ── App.tsx ────────────────────────────────────────────────────────────────────

def generar_app(modelo: dict):
    entidades = list(modelo.get("entities", {}).keys())

    imports_pages = "\n".join([
        "import LoginPage    from './pages/LoginPage'",
        "import RegisterPage from './pages/RegisterPage'",
        "import DashboardPage from './pages/DashboardPage'",
    ] + [f"import {e}Page from './pages/{e}Page'" for e in entidades if e not in ("LecturaSensor", "VerificationToken")] +
    ["import TaigaPage from './pages/TaigaPage'"])

    rutas = "\n".join([
        "          <Route path=\"dashboard\" element={<DashboardPage />} />",
    ] + [f"          <Route path=\"{e.lower()}s\" element={{<{e}Page />}} />" for e in entidades if e not in ("LecturaSensor", "VerificationToken")] +
    ["          <Route path=\"taiga\" element={<TaigaPage />} />"])

    contenido = f"""{HEADER_TS}
import {{ Routes, Route, Navigate }} from 'react-router-dom'
import Layout      from './components/layout/Layout'
import PrivateRoute from './components/PrivateRoute'
{imports_pages}

export default function App() {{
  return (
    <Routes>
      {{/* Rutas públicas */}}
      <Route path="/login"    element={{<LoginPage />}} />
      <Route path="/register" element={{<RegisterPage />}} />

      {{/* Rutas protegidas — requieren sesión activa */}}
      <Route element={{<PrivateRoute />}}>
        <Route element={{<Layout />}}>
          <Route path="/" element={{<Navigate to="/dashboard" replace />}} />
{rutas}
        </Route>
      </Route>

      {{/* Cualquier ruta desconocida → login */}}
      <Route path="*" element={{<Navigate to="/login" replace />}} />
    </Routes>
  )
}}
"""
    escribir(SRC / "App.tsx", contenido)


# ── i18n/index.ts ──────────────────────────────────────────────────────────────

def generar_i18n(modelo: dict):
    entidades = modelo.get("entities", {})

    # Genera traducciones de navegación por cada entidad
    nav_es = "\n".join([f"      {e.lower()}: '{e}s'," for e in entidades])
    nav_en = "\n".join([f"      {e.lower()}: '{e}s'," for e in entidades])

    contenido = f"""{HEADER_TS}
import i18n from 'i18next'
import {{ initReactI18next }} from 'react-i18next'

/**
 * Configuración de i18next con soporte bilingüe (español / inglés).
 * Cada entidad del modelo-json.json tiene su sección de traducciones.
 * Generado automáticamente desde docs/modelo-json.json.
 */

const resources = {{
  es: {{
    translation: {{
      common: {{
        loading:  'Cargando...',
        save:     'Guardar',
        cancel:   'Cancelar',
        edit:     'Editar',
        delete:   'Eliminar',
        actions:  'Acciones',
        noData:   'No hay datos disponibles',
        idioma:   'English',
        confirm:  '¿Confirmar eliminación?',
        search:   'Buscar...',
      }},
      nav: {{
        dashboard: 'Panel de Control',
{nav_es}
        taiga:     'Historias de Usuario',
        logout:    'Cerrar sesión',
      }},
      // Sección de Taiga
      taiga: {{
        title:           'Historias de Usuario',
        subtitle:        'Sincronizado con el proyecto en Taiga',
        sincronizar:     'Sincronizar',
        sincronizando:   'Sincronizando...',
        backlog:         'Backlog',
        total:           'Total',
        historias:       'historias',
        cerradas:        'Cerradas',
        abiertas:        'Abiertas',
        puntos:          'Story Points',
        noCredenciales:  'Las credenciales de Taiga no están configuradas.',
        noDisponible:    'La API de Taiga no está disponible.',
        verEnTaiga:      'Ver proyecto completo en Taiga',
        filtroTodo:      'Todas',
        filtroAbiertas:  'Abiertas',
        filtroCerradas:  'Cerradas',
        buscar:          'Buscar historia...',
      }},
    }},
  }},
  en: {{
    translation: {{
      common: {{
        loading:  'Loading...',
        save:     'Save',
        cancel:   'Cancel',
        edit:     'Edit',
        delete:   'Delete',
        actions:  'Actions',
        noData:   'No data available',
        idioma:   'Español',
        confirm:  'Confirm deletion?',
        search:   'Search...',
      }},
      nav: {{
        dashboard: 'Dashboard',
{nav_en}
        taiga:     'User Stories',
        logout:    'Log out',
      }},
      taiga: {{
        title:           'User Stories',
        subtitle:        'Synchronized with the Taiga project',
        sincronizar:     'Sync',
        sincronizando:   'Syncing...',
        backlog:         'Backlog',
        total:           'Total',
        historias:       'stories',
        cerradas:        'Closed',
        abiertas:        'Open',
        puntos:          'Story Points',
        noCredenciales:  'Taiga credentials are not configured.',
        noDisponible:    'The Taiga API is not available.',
        verEnTaiga:      'View full project in Taiga',
        filtroTodo:      'All',
        filtroAbiertas:  'Open',
        filtroCerradas:  'Closed',
        buscar:          'Search story...',
      }},
    }},
  }},
}}

i18n.use(initReactI18next).init({{
  resources,
  lng: 'es',
  fallbackLng: 'es',
  interpolation: {{ escapeValue: false }},
}})

export default i18n
"""
    escribir(SRC / "i18n" / "index.ts", contenido)


# ── Layout.tsx ─────────────────────────────────────────────────────────────────

def generar_layout():
    contenido = f"""{HEADER_TS}
import {{ Outlet, NavLink }} from 'react-router-dom'
import {{ useTranslation }} from 'react-i18next'
import {{
  LayoutDashboard, Map, Leaf, Bell, Wheat, Users, LogOut, Globe,
  Activity, AlertTriangle, BookOpen
}} from 'lucide-react'
import {{ useAuth }} from '../../context/AuthContext'

export default function Layout() {{
  const {{ t, i18n }} = useTranslation()
  const {{ isAdmin, user }} = useAuth()

  const toggleLang = () =>
    i18n.changeLanguage(i18n.language === 'es' ? 'en' : 'es')

  const handleLogout = async () => {{
    const API_BASE = import.meta.env.VITE_API_URL ?? '/api'
    try {{
      await fetch(`${{API_BASE}}/auth/logout`, {{ method: 'POST', credentials: 'include' }})
    }} catch (_) {{}} finally {{
      window.location.href = '/login'
    }}
  }}

  const navItems = [
    {{ to: '/dashboard',  icon: <LayoutDashboard size={{18}} />, label: t('nav.dashboard'),  adminOnly: false }},
    {{ to: '/zonas',      icon: <Map size={{18}} />,             label: t('nav.zona'),        adminOnly: false }},
    {{ to: '/plantas',    icon: <Leaf size={{18}} />,            label: t('nav.planta'),      adminOnly: false }},
    {{ to: '/sensores',   icon: <Activity size={{18}} />,        label: t('nav.sensor'),      adminOnly: false }},
    {{ to: '/alertas',    icon: <Bell size={{18}} />,            label: t('nav.alerta'),      adminOnly: false }},
    {{ to: '/cosechas',   icon: <Wheat size={{18}} />,           label: t('nav.cosecha'),     adminOnly: false }},
    {{ to: '/novedades',  icon: <AlertTriangle size={{18}} />,   label: t('nav.novedades'),   adminOnly: false }},
    {{ to: '/empleados',  icon: <Users size={{18}} />,           label: t('nav.empleado'),    adminOnly: true  }},
    {{ to: '/taiga',      icon: <BookOpen size={{18}} />,        label: t('nav.taiga'),       adminOnly: true  }},
  ].filter(item => !item.adminOnly || isAdmin)

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-60 bg-green-800 text-white flex flex-col">
        <div className="p-5 border-b border-green-700">
          <h1 className="text-xl font-bold">🌿 GreenHouse</h1>
          <p className="text-green-300 text-xs mt-1">Manager</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {{navItems.map(item => (
            <NavLink key={{item.to}} to={{item.to}}
              className={{({{ isActive }}) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${{
                  isActive ? 'bg-green-600 text-white' : 'text-green-200 hover:bg-green-700 hover:text-white'
                }}`
              }}>
              {{item.icon}}
              {{item.label}}
            </NavLink>
          ))}}
        </nav>
        <div className="p-3 border-t border-green-700 space-y-1">
          {{user && (
            <div className="px-3 py-2 text-xs text-green-300 truncate">
              <span className="font-medium text-white">{{user.email.split('@')[0]}}</span>
              <span className={{`ml-2 px-1.5 py-0.5 rounded text-white text-xs font-bold ${{
                user.rol === 'ADMINISTRADOR' ? 'bg-red-600' :
                user.rol === 'SUPERVISOR'    ? 'bg-blue-600' : 'bg-green-600'
              }}`}}>{{user.rol}}</span>
            </div>
          )}}
          <button onClick={{toggleLang}}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-green-200 hover:bg-green-700 hover:text-white w-full">
            <Globe size={{18}} />{{t('common.idioma')}}
          </button>
          <button onClick={{handleLogout}}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-green-200 hover:bg-green-700 hover:text-white w-full">
            <LogOut size={{18}} />{{t('nav.logout')}}
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  )
}}
"""
    escribir(SRC / "components" / "layout" / "Layout.tsx", contenido)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  GENERADOR FRONTEND REACT + VITE — GreenHouse Manager")
    print("=" * 60)

    modelo = json.loads(MODELO.read_text(encoding="utf-8"))
    entidades = modelo.get("entities", {})

    print(f"\n  Modelo: v{modelo.get('version','?')} — {len(entidades)} entidades\n")

    generar_package_json()
    generar_vite_config()
    generar_types(modelo)
    generar_api_service(modelo)
    generar_app(modelo)
    generar_i18n(modelo)
    generar_layout()

    # Indicar qué páginas se generarían (una por entidad)
    paginas = [e for e in entidades if e not in ("LecturaSensor", "VerificationToken")]
    paginas += ["Login", "Register", "Dashboard", "Novedades", "Taiga"]
    print(f"\n  Páginas a generar ({len(paginas)}):")
    for p in paginas:
        print(f"    - {p}Page.tsx  → src/pages/{p}Page.tsx")
        # En producción aquí iría: generar_pagina(p, entidades.get(p, {}))

    print(f"\n  ✓ Frontend generado en: {FRONTEND.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
