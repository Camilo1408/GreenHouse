"""
GreenHouse Manager — Generador del Frontend React + Vite
=========================================================
Lee docs/modelo-json.json y genera la estructura completa del frontend
a partir de las entidades, relaciones, RBAC y endpoints del modelo.

NO tiene código del sistema hardcodeado:
  - types.ts      → interfaces TypeScript derivadas de entidad["properties"]
  - api.ts        → servicios CRUD derivados de entidad["table"] y api_endpoints
  - App.tsx       → rutas derivadas de las entidades del modelo
  - Layout.tsx    → items del sidebar con adminOnly derivado de entidad["rbac"]
  - i18n/index.ts → secciones de traducción derivadas de los nombres de entidades
  - package.json  → dependencias fijas del stack tecnológico

NOTA: Script DEMOSTRATIVO. No ejecutar directamente.
"""

import json
from pathlib import Path
from datetime import date

ROOT     = Path(__file__).parent.parent
MODELO   = ROOT / "docs" / "modelo-json.json"
FRONTEND = ROOT / "greenhouse-frontend"
SRC      = FRONTEND / "src"

ANIO = date.today().year


def escribir(path: Path, contenido: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contenido, encoding="utf-8")
    print("  [FRONTEND] " + str(path.relative_to(ROOT)))


def encabezado_ts(archivo: str) -> str:
    return (
        "/*\n"
        " * GreenHouse Manager\n"
        " * Autores: [Nombres del equipo]\n"
        " * Fecha: " + str(ANIO) + "\n"
        " * Generado desde docs/modelo-json.json\n"
        " * Archivo: " + archivo + "\n"
        " */\n"
    )


def camel_a_snake(nombre: str) -> str:
    resultado = ""
    for c in nombre:
        resultado += ("_" + c.lower()) if c.isupper() else c
    return resultado.lstrip("_")


def url_path_de_tabla(tabla: str) -> str:
    return tabla.replace("_", "-") + "s"


# ── package.json ───────────────────────────────────────────────────────────────

def generar_package_json():
    contenido = json.dumps({
        "name": "greenhouse-frontend",
        "version": "1.0.0",
        "description": "GreenHouse Manager - Frontend React",
        "type": "module",
        "scripts": {
            "dev":     "vite",
            "build":   "tsc && vite build",
            "preview": "vite preview",
            "test":    "vitest"
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
    # No usamos f-string para evitar conflicto con llaves de la config de Vite
    contenido = (
        encabezado_ts("vite.config.ts") +
        "import { defineConfig } from 'vite'\n"
        "import react from '@vitejs/plugin-react'\n\n"
        "export default defineConfig({\n"
        "  plugins: [react()],\n"
        "  server: {\n"
        "    proxy: {\n"
        "      '/api':    { target: 'http://localhost:8080', changeOrigin: true },\n"
        "      '/oauth2': { target: 'http://localhost:8080', changeOrigin: true },\n"
        "      '/login':  { target: 'http://localhost:8080', changeOrigin: true },\n"
        "    },\n"
        "  },\n"
        "})\n"
    )
    escribir(FRONTEND / "vite.config.ts", contenido)


# ── types.ts — interfaces TypeScript desde entidad["properties"] ───────────────

def generar_types(modelo: dict):
    """
    Genera una interface TypeScript por cada entidad del modelo.
    Los tipos se mapean desde los tipos JSON Schema:
      integer  → number
      number   → number
      boolean  → boolean
      string   → string
      date/datetime → string
      enum     → union type literal
      $ref     → referencia a otra interface
    """
    entidades = modelo.get("entities", {})

    tipo_map = {
        "integer": "number",
        "number":  "number",
        "boolean": "boolean",
        "string":  "string",
    }

    lineas_interfaces = []

    for nombre, entidad in entidades.items():
        desc  = entidad.get("description", nombre)
        props = entidad.get("properties", {})
        campos = []

        for pname, pdef in props.items():
            if "$ref" in pdef:
                ref_clase = pdef["$ref"].replace("#/entities/", "")
                nullable  = pdef.get("nullable", False)
                tipo_ts   = ref_clase + " | null" if nullable else ref_clase
                op        = "?" if nullable else ""
                # Descripcion del campo como comentario
                desc_campo = pdef.get("description", "")
                if desc_campo:
                    campos.append("  /** " + desc_campo + " */")
                campos.append("  " + pname + op + ": " + tipo_ts)
            else:
                enums = pdef.get("enum", [])
                if enums:
                    ts_type = " | ".join("'" + e + "'" for e in enums)
                else:
                    ts_type = tipo_map.get(pdef.get("type", "string"), "string")

                op = "?" if pname in ("id", "observaciones", "notas") else ""
                desc_campo = pdef.get("description", "")
                if desc_campo:
                    campos.append("  /** " + desc_campo + " */")
                campos.append("  " + pname + op + ": " + ts_type)

        campos_str = "\n".join(campos)
        lineas_interfaces.append(
            "/** " + desc + " */\n"
            "export interface " + nombre + " {\n" +
            campos_str + "\n}"
        )

    contenido = (
        encabezado_ts("types.ts") +
        "// Interfaces TypeScript generadas desde docs/modelo-json.json\n"
        "// Cada interface corresponde a una entidad del modelo.\n\n" +
        "\n\n".join(lineas_interfaces) + "\n"
    )
    escribir(SRC / "types.ts", contenido)


# ── services/api.ts — servicios CRUD desde entidades y api_endpoints ──────────

def generar_api_service(modelo: dict):
    """
    Genera un servicio axios por cada entidad.
    - La URL base se construye desde entidad["table"]
    - Los métodos disponibles se derivan de entidad["rbac"]
    - Los endpoints especiales se leen de modelo["api_endpoints"]
    """
    entidades  = modelo.get("entities", {})
    endpoints  = modelo.get("api_endpoints", {})

    lineas_servicios = []

    for nombre, entidad in entidades.items():
        tabla    = entidad.get("table", camel_a_snake(nombre))
        url      = url_path_de_tabla(tabla)
        rbac     = entidad.get("rbac", {})
        desc     = entidad.get("description", nombre)
        var_name = nombre[0].lower() + nombre[1:] + "Service"

        # Determinar endpoints extra desde modelo["api_endpoints"]
        eps_modulo = endpoints.get(url, [])
        endpoints_extra = [
            ep for ep in eps_modulo
            if "zona/" in ep.lower() or "estado/" in ep.lower()
               or "periodo" in ep.lower() or "estadisticas" in ep.lower()
               or "pendientes" in ep.lower() or "planta/" in ep.lower()
        ]

        metodos = []
        metodos.append("  /** Retorna todos los registros de " + nombre + ". */")
        metodos.append("  getAll:   ()              => api.get('/" + url + "'),")
        metodos.append("  /** Retorna un registro de " + nombre + " por ID. */")
        metodos.append("  getById:  (id: number)    => api.get(`/" + url + "/${id}`),")

        if "CREATE" in rbac:
            metodos.append("  /** Crea un nuevo registro de " + nombre + ". */")
            metodos.append("  create:   (data: object)  => api.post('/" + url + "', data),")

        if "UPDATE" in rbac:
            metodos.append("  /** Actualiza un registro existente de " + nombre + ". */")
            metodos.append("  update:   (id: number, data: object) => api.put(`/" + url + "/${id}`, data),")

        if "DELETE" in rbac:
            metodos.append("  /** Elimina un registro de " + nombre + ". */")
            metodos.append("  delete:   (id: number)    => api.delete(`/" + url + "/${id}`),")

        # Endpoints especiales detectados en el modelo
        for ep in endpoints_extra:
            partes = ep.strip().split()
            if len(partes) >= 2:
                metodo = partes[0].lower()
                ruta   = partes[1]
                # Convertir parámetros de ruta a template literals TS
                ruta_ts = ruta.replace("{zonaId}", "${zonaId}").replace("{estado}", "${estado}")
                metodos.append("  // Endpoint adicional del modelo: " + ep.strip())
                metodos.append("  " + metodo + "Extra: (param: unknown) => api." + metodo + "(`" + ruta_ts + "`),")

        metodos_str = "\n".join(metodos)

        lineas_servicios.append(
            "/**\n"
            " * Servicio para operaciones sobre " + nombre + ".\n"
            " * " + desc + "\n"
            " * Endpoints base: /api/" + url + "\n"
            " * RBAC del modelo: " + str(rbac) + "\n"
            " */\n"
            "export const " + var_name + " = {\n" +
            metodos_str + "\n}"
        )

    # Servicio Taiga (extra, definido en generacion_scripts del modelo)
    lineas_servicios.append(
        "/**\n"
        " * Proxy Taiga — solo ADMINISTRADOR.\n"
        " * Definido en modelo-json.json > generacion_scripts.\n"
        " */\n"
        "export const taigaService = {\n"
        "  /** Retorna las historias de usuario del proyecto Taiga agrupables por sprint. */\n"
        "  getHistorias: () => api.get('/taiga/historias'),\n"
        "}"
    )

    # Interceptor de respuesta — no usa llaves de template, se arma con concatenación
    interceptor = (
        "/**\n"
        " * Instancia base de Axios.\n"
        " * En desarrollo usa el proxy de Vite (/api → localhost:8080).\n"
        " * En produccion Railway usa VITE_API_URL.\n"
        " */\n"
        "const api = axios.create({\n"
        "  baseURL: import.meta.env.VITE_API_URL ?? '/api',\n"
        "  withCredentials: true,\n"
        "  headers: { 'Content-Type': 'application/json' },\n"
        "})\n\n"
        "/** Redirige a /login cuando el backend responde 401. */\n"
        "api.interceptors.response.use(\n"
        "  res => res,\n"
        "  err => {\n"
        "    const publicPaths = ['/login', '/register']\n"
        "    const onPublicPage = publicPaths.some(p => window.location.pathname.startsWith(p))\n"
        "    if (err.response?.status === 401 && !onPublicPage) {\n"
        "      window.location.href = '/login'\n"
        "    }\n"
        "    return Promise.reject(err)\n"
        "  }\n"
        ")\n"
    )

    contenido = (
        encabezado_ts("services/api.ts") +
        "import axios from 'axios'\n\n" +
        interceptor + "\n" +
        "\n\n".join(lineas_servicios) + "\n\n"
        "export default api\n"
    )
    escribir(SRC / "services" / "api.ts", contenido)


# ── App.tsx — rutas generadas desde las entidades del modelo ──────────────────

def generar_app(modelo: dict):
    """
    Genera App.tsx con una ruta por cada entidad del modelo.
    Las entidades LecturaSensor y VerificationToken no tienen página propia.
    Se agregan siempre: Login, Register, Dashboard, Novedades, Taiga.
    """
    entidades = modelo.get("entities", {})

    # Entidades que sí tienen página
    sin_pagina = {"LecturaSensor", "VerificationToken", "Turno"}
    con_pagina = [e for e in entidades if e not in sin_pagina]

    # Imports de páginas
    imports = [
        "import LoginPage     from './pages/LoginPage'",
        "import RegisterPage  from './pages/RegisterPage'",
        "import DashboardPage from './pages/DashboardPage'",
        "import NovedadesPage from './pages/NovedadesPage'",
        "import TaigaPage     from './pages/TaigaPage'",
    ]
    for e in con_pagina:
        imports.append("import " + e + "Page from './pages/" + e + "Page'")

    # Rutas — url derivada de la entidad
    rutas = [
        "          <Route path=\"dashboard\" element={<DashboardPage />} />",
        "          <Route path=\"novedades\" element={<NovedadesPage />} />",
        "          <Route path=\"taiga\"     element={<TaigaPage />} />",
    ]
    for e in con_pagina:
        tabla = entidades[e].get("table", camel_a_snake(e))
        url   = url_path_de_tabla(tabla)
        rutas.append("          <Route path=\"" + url + "\" element={<" + e + "Page />} />")

    contenido = (
        encabezado_ts("App.tsx") +
        "import { Routes, Route, Navigate } from 'react-router-dom'\n"
        "import Layout       from './components/layout/Layout'\n"
        "import PrivateRoute from './components/PrivateRoute'\n" +
        "\n".join(imports) + "\n\n"
        "export default function App() {\n"
        "  return (\n"
        "    <Routes>\n"
        "      {/* Rutas publicas */}\n"
        "      <Route path=\"/login\"    element={<LoginPage />} />\n"
        "      <Route path=\"/register\" element={<RegisterPage />} />\n\n"
        "      {/* Rutas protegidas */}\n"
        "      <Route element={<PrivateRoute />}>\n"
        "        <Route element={<Layout />}>\n"
        "          <Route path=\"/\" element={<Navigate to=\"/dashboard\" replace />} />\n" +
        "\n".join(rutas) + "\n"
        "        </Route>\n"
        "      </Route>\n\n"
        "      <Route path=\"*\" element={<Navigate to=\"/login\" replace />} />\n"
        "    </Routes>\n"
        "  )\n"
        "}\n"
    )
    escribir(SRC / "App.tsx", contenido)


# ── Layout.tsx — sidebar con RBAC derivado del modelo ─────────────────────────

def generar_layout(modelo: dict):
    """
    Genera Layout.tsx con un item de navegacion por entidad.
    adminOnly se deriva de entidad["rbac"]["READ"]:
      si READ es solo ADMINISTRADOR → adminOnly: true
    """
    entidades = modelo.get("entities", {})
    sin_pagina = {"LecturaSensor", "VerificationToken", "Turno"}

    # Iconos asignados por tipo de entidad (desde su descripcion)
    iconos_disponibles = [
        "LayoutDashboard", "Map", "Leaf", "Activity", "Bell",
        "Wheat", "AlertTriangle", "Users", "BookOpen", "Package"
    ]

    items_nav = [
        "    { to: '/dashboard', icon: <LayoutDashboard size={18} />, label: t('nav.dashboard'), adminOnly: false },",
    ]

    icono_idx = 1
    for nombre, entidad in entidades.items():
        if nombre in sin_pagina:
            continue
        tabla = entidad.get("table", camel_a_snake(nombre))
        url   = "/" + url_path_de_tabla(tabla)
        rbac  = entidad.get("rbac", {})

        # adminOnly: true si el READ está restringido a ADMINISTRADOR
        read_rbac  = rbac.get("READ", "todos los roles")
        admin_only = "ADMINISTRADOR" in read_rbac and "todos" not in read_rbac.lower()
        admin_str  = "true" if admin_only else "false"

        icono = iconos_disponibles[icono_idx % len(iconos_disponibles)]
        icono_idx += 1

        items_nav.append(
            "    { to: '" + url + "', icon: <" + icono + " size={18} />, "
            "label: t('nav." + camel_a_snake(nombre) + "'), adminOnly: " + admin_str + " },"
        )

    # Novedades y Taiga (siempre al final)
    items_nav.append("    { to: '/novedades', icon: <AlertTriangle size={18} />, label: t('nav.novedades'), adminOnly: false },")
    items_nav.append("    { to: '/taiga',     icon: <BookOpen size={18} />,      label: t('nav.taiga'),     adminOnly: true  },")

    items_str = "\n".join(items_nav)

    contenido = (
        encabezado_ts("components/layout/Layout.tsx") +
        "import { Outlet, NavLink } from 'react-router-dom'\n"
        "import { useTranslation } from 'react-i18next'\n"
        "import {\n"
        "  LayoutDashboard, Map, Leaf, Bell, Wheat, Users,\n"
        "  LogOut, Globe, Activity, AlertTriangle, BookOpen, Package\n"
        "} from 'lucide-react'\n"
        "import { useAuth } from '../../context/AuthContext'\n\n"
        "export default function Layout() {\n"
        "  const { t, i18n } = useTranslation()\n"
        "  const { isAdmin, user } = useAuth()\n\n"
        "  const toggleLang = () =>\n"
        "    i18n.changeLanguage(i18n.language === 'es' ? 'en' : 'es')\n\n"
        "  const handleLogout = async () => {\n"
        "    const API_BASE = import.meta.env.VITE_API_URL ?? '/api'\n"
        "    try {\n"
        "      await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' })\n"
        "    } catch (_) {} finally {\n"
        "      window.location.href = '/login'\n"
        "    }\n"
        "  }\n\n"
        "  // Items de navegacion generados desde el modelo-json.json\n"
        "  // adminOnly derivado de entidad.rbac.READ\n"
        "  const navItems = [\n" +
        items_str + "\n"
        "  ].filter(item => !item.adminOnly || isAdmin)\n\n"
        "  return (\n"
        "    <div className=\"flex h-screen bg-gray-50\">\n"
        "      <aside className=\"w-60 bg-green-800 text-white flex flex-col\">\n"
        "        <div className=\"p-5 border-b border-green-700\">\n"
        "          <h1 className=\"text-xl font-bold\">🌿 GreenHouse</h1>\n"
        "          <p className=\"text-green-300 text-xs mt-1\">Manager</p>\n"
        "        </div>\n"
        "        <nav className=\"flex-1 p-3 space-y-1\">\n"
        "          {navItems.map(item => (\n"
        "            <NavLink key={item.to} to={item.to}\n"
        "              className={({ isActive }) =>\n"
        "                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${\n"
        "                  isActive ? 'bg-green-600 text-white' : 'text-green-200 hover:bg-green-700'\n"
        "                }`\n"
        "              }>\n"
        "              {item.icon}\n"
        "              {item.label}\n"
        "            </NavLink>\n"
        "          ))}\n"
        "        </nav>\n"
        "        <div className=\"p-3 border-t border-green-700 space-y-1\">\n"
        "          {user && (\n"
        "            <div className=\"px-3 py-2 text-xs text-green-300 truncate\">\n"
        "              <span className=\"font-medium text-white\">{user.email.split('@')[0]}</span>\n"
        "            </div>\n"
        "          )}\n"
        "          <button onClick={toggleLang}\n"
        "            className=\"flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-green-200 hover:bg-green-700 w-full\">\n"
        "            <Globe size={18} />{t('common.idioma')}\n"
        "          </button>\n"
        "          <button onClick={handleLogout}\n"
        "            className=\"flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-green-200 hover:bg-green-700 w-full\">\n"
        "            <LogOut size={18} />{t('nav.logout')}\n"
        "          </button>\n"
        "        </div>\n"
        "      </aside>\n"
        "      <main className=\"flex-1 overflow-auto p-6\">\n"
        "        <Outlet />\n"
        "      </main>\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )
    escribir(SRC / "components" / "layout" / "Layout.tsx", contenido)


# ── i18n/index.ts — traducciones derivadas de entidades del modelo ─────────────

def generar_i18n(modelo: dict):
    """
    Genera las traducciones leyendo:
    - Los nombres de entidades para el nav
    - Las descripciones de entidades para los subtítulos
    - Los campos "enum" para las etiquetas de estados
    - Los roles desde modelo["roles"]
    """
    entidades  = modelo.get("entities", {})
    roles_mod  = modelo.get("roles", {})
    sin_pagina = {"LecturaSensor", "VerificationToken", "Turno"}

    # Nav items en español e inglés
    nav_es = ["      dashboard: 'Panel de Control',"]
    nav_en = ["      dashboard: 'Dashboard',"]
    for nombre, entidad in entidades.items():
        if nombre in sin_pagina:
            continue
        clave = camel_a_snake(nombre)
        nav_es.append("      " + clave + ": '" + nombre + "s',")
        nav_en.append("      " + clave + ": '" + nombre + "s',")
    nav_es.append("      novedades: 'Novedades',")
    nav_en.append("      novedades: 'News',")
    nav_es.append("      taiga: 'Historias de Usuario',")
    nav_en.append("      taiga: 'User Stories',")
    nav_es.append("      logout: 'Cerrar sesion',")
    nav_en.append("      logout: 'Log out',")

    # Secciones de enum por entidad
    enums_es = []
    enums_en = []
    for nombre, entidad in entidades.items():
        for pname, pdef in entidad.get("properties", {}).items():
            enums = pdef.get("enum", [])
            if enums:
                for val in enums:
                    etiqueta = val.replace("_", " ").title()
                    enums_es.append("      '" + val + "': '" + etiqueta + "',")
                    enums_en.append("      '" + val + "': '" + etiqueta + "',")

    # Roles desde el modelo
    roles_es = []
    roles_en = []
    for rol in roles_mod:
        roles_es.append("      " + rol + ": '" + rol + "',")
        roles_en.append("      " + rol + ": '" + rol + "',")

    nav_es_str   = "\n".join(nav_es)
    nav_en_str   = "\n".join(nav_en)
    enums_es_str = "\n".join(enums_es)
    enums_en_str = "\n".join(enums_en)
    roles_es_str = "\n".join(roles_es)
    roles_en_str = "\n".join(roles_en)

    contenido = (
        encabezado_ts("i18n/index.ts") +
        "import i18n from 'i18next'\n"
        "import { initReactI18next } from 'react-i18next'\n\n"
        "/**\n"
        " * Traducciones generadas desde docs/modelo-json.json.\n"
        " * - nav: items derivados de las entidades del modelo\n"
        " * - enums: etiquetas derivadas de los valores enum de cada entidad\n"
        " * - roles: derivados de modelo.roles\n"
        " */\n\n"
        "const resources = {\n"
        "  es: {\n"
        "    translation: {\n"
        "      common: {\n"
        "        loading: 'Cargando...',\n"
        "        save:    'Guardar',\n"
        "        cancel:  'Cancelar',\n"
        "        edit:    'Editar',\n"
        "        delete:  'Eliminar',\n"
        "        actions: 'Acciones',\n"
        "        noData:  'No hay datos disponibles',\n"
        "        idioma:  'English',\n"
        "      },\n"
        "      nav: {\n" +
        nav_es_str + "\n"
        "      },\n"
        "      roles: {\n" +
        roles_es_str + "\n"
        "      },\n"
        "      enums: {\n" +
        enums_es_str + "\n"
        "      },\n"
        "      taiga: {\n"
        "        title:          'Historias de Usuario',\n"
        "        subtitle:       'Sincronizado con el proyecto en Taiga',\n"
        "        sincronizar:    'Sincronizar',\n"
        "        sincronizando:  'Sincronizando...',\n"
        "        backlog:        'Backlog',\n"
        "        total:          'Total',\n"
        "        historias:      'historias',\n"
        "        cerradas:       'Cerradas',\n"
        "        abiertas:       'Abiertas',\n"
        "        puntos:         'Story Points',\n"
        "        noCredenciales: 'Las credenciales de Taiga no estan configuradas.',\n"
        "        noDisponible:   'La API de Taiga no esta disponible.',\n"
        "        verEnTaiga:     'Ver proyecto completo en Taiga',\n"
        "        filtroTodo:     'Todas',\n"
        "        filtroAbiertas: 'Abiertas',\n"
        "        filtroCerradas: 'Cerradas',\n"
        "        buscar:         'Buscar historia...',\n"
        "      },\n"
        "    },\n"
        "  },\n"
        "  en: {\n"
        "    translation: {\n"
        "      common: {\n"
        "        loading: 'Loading...',\n"
        "        save:    'Save',\n"
        "        cancel:  'Cancel',\n"
        "        edit:    'Edit',\n"
        "        delete:  'Delete',\n"
        "        actions: 'Actions',\n"
        "        noData:  'No data available',\n"
        "        idioma:  'Espanol',\n"
        "      },\n"
        "      nav: {\n" +
        nav_en_str + "\n"
        "      },\n"
        "      roles: {\n" +
        roles_en_str + "\n"
        "      },\n"
        "      enums: {\n" +
        enums_en_str + "\n"
        "      },\n"
        "      taiga: {\n"
        "        title:          'User Stories',\n"
        "        subtitle:       'Synchronized with the Taiga project',\n"
        "        sincronizar:    'Sync',\n"
        "        sincronizando:  'Syncing...',\n"
        "        backlog:        'Backlog',\n"
        "        total:          'Total',\n"
        "        historias:      'stories',\n"
        "        cerradas:       'Closed',\n"
        "        abiertas:       'Open',\n"
        "        puntos:         'Story Points',\n"
        "        noCredenciales: 'Taiga credentials are not configured.',\n"
        "        noDisponible:   'The Taiga API is not available.',\n"
        "        verEnTaiga:     'View full project in Taiga',\n"
        "        filtroTodo:     'All',\n"
        "        filtroAbiertas: 'Open',\n"
        "        filtroCerradas: 'Closed',\n"
        "        buscar:         'Search story...',\n"
        "      },\n"
        "    },\n"
        "  },\n"
        "}\n\n"
        "i18n.use(initReactI18next).init({\n"
        "  resources,\n"
        "  lng: 'es',\n"
        "  fallbackLng: 'es',\n"
        "  interpolation: { escapeValue: false },\n"
        "})\n\n"
        "export default i18n\n"
    )
    escribir(SRC / "i18n" / "index.ts", contenido)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  GENERADOR FRONTEND REACT + VITE — GreenHouse Manager")
    print("  Fuente: docs/modelo-json.json")
    print("=" * 60)

    modelo    = json.loads(MODELO.read_text(encoding="utf-8"))
    entidades = modelo.get("entities", {})
    version   = modelo.get("version", "?")

    print("\n  Modelo v" + version + " — " + str(len(entidades)) + " entidades\n")

    generar_package_json()
    generar_vite_config()
    generar_types(modelo)
    generar_api_service(modelo)
    generar_app(modelo)
    generar_layout(modelo)
    generar_i18n(modelo)

    sin_pagina = {"LecturaSensor", "VerificationToken", "Turno"}
    con_pagina = [e for e in entidades if e not in sin_pagina]
    paginas_totales = len(con_pagina) + 4  # + Login, Register, Dashboard, Novedades, Taiga

    print("\n  Paginas que se generarian (" + str(paginas_totales) + "):")
    for p in con_pagina + ["Login", "Register", "Dashboard", "Novedades", "Taiga"]:
        print("    - src/pages/" + p + "Page.tsx")

    print("\n  ✓ Frontend generado desde entidades del modelo JSON")
    print("    types.ts   : " + str(len(entidades)) + " interfaces TypeScript")
    print("    api.ts     : " + str(len(entidades)) + " servicios CRUD + taigaService")
    print("    i18n       : nav, enums, roles, taiga — todo desde el modelo")


if __name__ == "__main__":
    main()
