/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { Outlet, NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  LayoutDashboard, Map, Leaf, Bell, Wheat, Users, LogOut, Globe, Activity, AlertTriangle
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export default function Layout() {
  const { t, i18n } = useTranslation()
  const { isAdmin, user } = useAuth()

  const toggleLang = () =>
    i18n.changeLanguage(i18n.language === 'es' ? 'en' : 'es')

  const handleLogout = async () => {
    const API_BASE = import.meta.env.VITE_API_URL ?? '/api'
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })
    } catch (_) {
      // Si falla la llamada igual cerramos sesión en el frontend
    } finally {
      // Full page reload clears AuthContext state completely,
      // preventing the previous user's data from appearing on next login.
      window.location.href = '/login'
    }
  }

  const navItems = [
    { to: '/dashboard', icon: <LayoutDashboard size={18} />, label: t('nav.dashboard'), adminOnly: false },
    { to: '/zonas',     icon: <Map size={18} />,             label: t('nav.zonas'),     adminOnly: false },
    { to: '/plantas',   icon: <Leaf size={18} />,            label: t('nav.plantas'),   adminOnly: false },
    { to: '/sensores',  icon: <Activity size={18} />,        label: t('nav.sensores'),  adminOnly: false },
    { to: '/alertas',   icon: <Bell size={18} />,            label: t('nav.alertas'),   adminOnly: false },
    { to: '/cosechas',   icon: <Wheat size={18} />,          label: t('nav.cosechas'),   adminOnly: false },
    { to: '/novedades',  icon: <AlertTriangle size={18} />, label: t('nav.novedades'),  adminOnly: false },
    { to: '/empleados',  icon: <Users size={18} />,         label: t('nav.empleados'),  adminOnly: true  },
  ].filter(item => !item.adminOnly || isAdmin)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-60 bg-green-800 text-white flex flex-col">
        <div className="p-5 border-b border-green-700">
          <h1 className="text-xl font-bold">🌿 GreenHouse</h1>
          <p className="text-green-300 text-xs mt-1">Manager</p>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-green-600 text-white'
                    : 'text-green-200 hover:bg-green-700 hover:text-white'
                }`
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-green-700 space-y-1">
          {user && (
            <div className="px-3 py-2 text-xs text-green-300 truncate">
              <span className="font-medium text-white">{user.email.split('@')[0]}</span>
              <span className={`ml-2 px-1.5 py-0.5 rounded text-white text-xs font-bold ${
                user.rol === 'ADMINISTRADOR' ? 'bg-red-600' :
                user.rol === 'SUPERVISOR' ? 'bg-blue-600' : 'bg-green-600'
              }`}>{user.rol}</span>
            </div>
          )}
          <button
            onClick={toggleLang}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-green-200 hover:bg-green-700 hover:text-white w-full transition-colors"
          >
            <Globe size={18} />
            {i18n.language === 'es' ? 'English' : 'Español'}
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-green-200 hover:bg-green-700 hover:text-white w-full transition-colors"
          >
            <LogOut size={18} />
            {t('nav.logout')}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  )
}
