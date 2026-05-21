/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { Outlet, NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  LayoutDashboard, Map, Leaf, Bell, Wheat, Users, LogOut, Globe
} from 'lucide-react'

export default function Layout() {
  const { t, i18n } = useTranslation()

  const toggleLang = () =>
    i18n.changeLanguage(i18n.language === 'es' ? 'en' : 'es')

  const navItems = [
    { to: '/dashboard', icon: <LayoutDashboard size={18} />, label: t('nav.dashboard') },
    { to: '/zonas',     icon: <Map size={18} />,             label: t('nav.zonas') },
    { to: '/plantas',   icon: <Leaf size={18} />,            label: t('nav.plantas') },
    { to: '/alertas',   icon: <Bell size={18} />,            label: t('nav.alertas') },
    { to: '/cosechas',  icon: <Wheat size={18} />,           label: t('nav.cosechas') },
    { to: '/empleados', icon: <Users size={18} />,           label: t('nav.empleados') },
  ]

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
          <button
            onClick={toggleLang}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-green-200 hover:bg-green-700 hover:text-white w-full transition-colors"
          >
            <Globe size={18} />
            {i18n.language === 'es' ? 'English' : 'Español'}
          </button>
          <a
            href="http://localhost:8080/logout"
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-green-200 hover:bg-green-700 hover:text-white transition-colors"
          >
            <LogOut size={18} />
            {t('nav.logout')}
          </a>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  )
}
