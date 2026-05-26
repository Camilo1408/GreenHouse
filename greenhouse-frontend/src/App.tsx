/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import PrivateRoute from './components/PrivateRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ZonasPage from './pages/ZonasPage'
import ZonaDetallePage from './pages/ZonaDetallePage'
import PlantasPage from './pages/PlantasPage'
import SensoresPage from './pages/SensoresPage'
import AlertasPage from './pages/AlertasPage'
import CosechasPage from './pages/CosechasPage'
import EmpleadosPage from './pages/EmpleadosPage'

export default function App() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/login"    element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Rutas protegidas — requieren sesión activa */}
      <Route element={<PrivateRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"        element={<DashboardPage />} />
          <Route path="zonas"            element={<ZonasPage />} />
          <Route path="zonas/:id"        element={<ZonaDetallePage />} />
          <Route path="plantas"          element={<PlantasPage />} />
          <Route path="sensores"         element={<SensoresPage />} />
          <Route path="alertas"          element={<AlertasPage />} />
          <Route path="cosechas"         element={<CosechasPage />} />
          <Route path="empleados"        element={<EmpleadosPage />} />
        </Route>
      </Route>

      {/* Cualquier ruta desconocida → login */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
