/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useEffect, useState } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import axios from 'axios'

/**
 * Protege las rutas internas verificando que el usuario
 * tenga una sesión activa en el backend (/api/auth/me).
 * Si no hay sesión, redirige a /login.
 */
export default function PrivateRoute() {
  const [status, setStatus] = useState<'checking' | 'auth' | 'unauth'>('checking')

  useEffect(() => {
    axios.get('/api/auth/me', { withCredentials: true })
      .then(() => setStatus('auth'))
      .catch(() => setStatus('unauth'))
  }, [])

  if (status === 'checking') {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-green-700 text-lg font-medium animate-pulse">
          🌿 Cargando GreenHouse...
        </div>
      </div>
    )
  }

  return status === 'auth' ? <Outlet /> : <Navigate to="/login" replace />
}
