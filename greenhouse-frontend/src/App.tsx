/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ZonasPage from './pages/ZonasPage'
import PlantasPage from './pages/PlantasPage'
import AlertasPage from './pages/AlertasPage'
import CosechasPage from './pages/CosechasPage'
import EmpleadosPage from './pages/EmpleadosPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login"    element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="zonas"     element={<ZonasPage />} />
        <Route path="plantas"   element={<PlantasPage />} />
        <Route path="alertas"   element={<AlertasPage />} />
        <Route path="cosechas"  element={<CosechasPage />} />
        <Route path="empleados" element={<EmpleadosPage />} />
      </Route>
    </Routes>
  )
}
