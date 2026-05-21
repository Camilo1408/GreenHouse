/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const [form, setForm] = useState({ nombreCompleto: '', email: '', password: '', confirmar: '' })
  const [loading, setLoading] = useState(false)
  const [registrado, setRegistrado] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmar, setShowConfirmar] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (form.password !== form.confirmar) {
      toast.error('Las contraseñas no coinciden')
      return
    }
    if (form.password.length < 8) {
      toast.error('La contraseña debe tener al menos 8 caracteres')
      return
    }

    setLoading(true)
    try {
      await axios.post('/api/auth/register', {
        nombreCompleto: form.nombreCompleto,
        email: form.email,
        password: form.password,
      }, { withCredentials: true })

      setRegistrado(true)
    } catch (err: any) {
      const msg = err.response?.data?.mensaje || 'Error al registrar. Intenta de nuevo.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  if (registrado) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-800 to-green-600 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md text-center">
          <div className="text-6xl mb-4">📧</div>
          <h2 className="text-2xl font-bold text-green-800 mb-3">¡Registro exitoso!</h2>
          <p className="text-gray-600 mb-2">
            Te enviamos un correo de verificación a <strong>{form.email}</strong>.
          </p>
          <p className="text-gray-500 text-sm mb-6">
            Revisa tu bandeja de entrada (y la carpeta de spam) y haz clic en el enlace para activar tu cuenta.
          </p>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800 mb-6">
            ⚠️ El enlace expira en <strong>24 horas</strong>.
          </div>
          <Link
            to="/login"
            className="inline-block bg-green-700 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-green-800 transition-colors"
          >
            Ir al inicio de sesión
          </Link>
          <p className="text-xs text-gray-400 mt-4">
            ¿No recibiste el correo?{' '}
            <button
              onClick={async () => {
                await axios.post(`/api/auth/resend-verification?email=${form.email}`)
                toast.success('Correo reenviado')
              }}
              className="text-green-700 underline"
            >
              Reenviar verificación
            </button>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-800 to-green-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">

        <div className="text-center mb-6">
          <div className="text-5xl mb-3">🌿</div>
          <h1 className="text-2xl font-bold text-green-800">Crear cuenta</h1>
          <p className="text-gray-500 text-sm mt-1">GreenHouse Manager</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre completo</label>
            <input
              type="text"
              required
              value={form.nombreCompleto}
              onChange={e => setForm({ ...form, nombreCompleto: e.target.value })}
              placeholder="Juan Pérez"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Correo electrónico</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              placeholder="tu@correo.com"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                placeholder="Mínimo 8 caracteres"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña</label>
            <div className="relative">
              <input
                type={showConfirmar ? 'text' : 'password'}
                required
                value={form.confirmar}
                onChange={e => setForm({ ...form, confirmar: e.target.value })}
                placeholder="Repite tu contraseña"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button
                type="button"
                onClick={() => setShowConfirmar(!showConfirmar)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                tabIndex={-1}
              >
                {showConfirmar ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* Indicador de seguridad de contraseña */}
          {form.password && (
            <div className="text-xs">
              <div className="flex gap-1 mb-1">
                {[1,2,3,4].map(i => (
                  <div key={i} className={`h-1 flex-1 rounded ${
                    form.password.length >= i * 3
                      ? i <= 2 ? 'bg-red-400' : i === 3 ? 'bg-yellow-400' : 'bg-green-500'
                      : 'bg-gray-200'
                  }`} />
                ))}
              </div>
              <span className="text-gray-500">
                {form.password.length < 6 ? 'Muy débil' :
                 form.password.length < 9 ? 'Débil' :
                 form.password.length < 12 ? 'Buena' : 'Fuerte'}
              </span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50 mt-2"
          >
            {loading ? 'Creando cuenta...' : 'Crear cuenta'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-5">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-green-700 font-semibold hover:underline">
            Inicia sesión
          </Link>
        </p>
      </div>
    </div>
  )
}
