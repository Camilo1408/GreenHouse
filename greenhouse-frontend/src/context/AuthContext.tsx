/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import api from '../services/api'

export type Rol = 'ADMINISTRADOR' | 'SUPERVISOR' | 'EMPLEADO'

interface AuthUser {
  email: string
  rol: Rol
}

interface AuthContextValue {
  user: AuthUser | null
  loading: boolean
  isAdmin: boolean
  isSupervisor: boolean
  isEmpleado: boolean
  /** True if the user can create/edit resources (ADMIN or SUPERVISOR) */
  canWrite: boolean
  /** True if only ADMIN can perform the action */
  isAdminOnly: boolean
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: true,
  isAdmin: false,
  isSupervisor: false,
  isEmpleado: false,
  canWrite: false,
  isAdminOnly: false,
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/auth/me')
      .then(r => {
        if (r.data?.exito) {
          setUser({ email: r.data.email, rol: r.data.rol })
        }
      })
      .catch(() => {
        // Not authenticated — PrivateRoute will redirect
      })
      .finally(() => setLoading(false))
  }, [])

  const isAdmin = user?.rol === 'ADMINISTRADOR'
  const isSupervisor = user?.rol === 'SUPERVISOR'
  const isEmpleado = user?.rol === 'EMPLEADO'
  const canWrite = isAdmin || isSupervisor
  const isAdminOnly = isAdmin

  return (
    <AuthContext.Provider value={{ user, loading, isAdmin, isSupervisor, isEmpleado, canWrite, isAdminOnly }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
