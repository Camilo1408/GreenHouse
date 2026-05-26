/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { zonaService, plantaService, alertaService, tratamientoService, empleadoService } from '../services/api'
import toast from 'react-hot-toast'
import type { Zona, Planta, Empleado } from '../types'
import { AlertTriangle, Leaf, CheckCircle } from 'lucide-react'

type TipoNovedad = 'ENFERMEDAD_PLANTA' | 'FALLA_ZONA'

const severidades = ['BAJA', 'MEDIA', 'ALTA', 'CRITICA'] as const

const severidadColor: Record<string, string> = {
  BAJA:    'bg-blue-100 text-blue-800 border-blue-200',
  MEDIA:   'bg-yellow-100 text-yellow-800 border-yellow-200',
  ALTA:    'bg-orange-100 text-orange-800 border-orange-200',
  CRITICA: 'bg-red-100 text-red-800 border-red-200',
}

export default function NovedadesPage() {
  const qc = useQueryClient()

  const [tipo, setTipo] = useState<TipoNovedad>('ENFERMEDAD_PLANTA')
  const [zonaId, setZonaId] = useState('')
  const [plantaId, setPlantaId] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [severidad, setSeveridad] = useState<string>('MEDIA')
  const [submitted, setSubmitted] = useState(false)

  const { data: zonas = [] } = useQuery<Zona[]>({
    queryKey: ['zonas'],
    queryFn: () => zonaService.getAll().then(r => r.data),
  })

  const { data: plantas = [] } = useQuery<Planta[]>({
    queryKey: ['plantas'],
    queryFn: () => plantaService.getAll().then(r => r.data),
  })

  // Get own employee profile for auto-attribution
  const { data: miEmpleado } = useQuery<Empleado | null>({
    queryKey: ['empleados-me'],
    queryFn: () => empleadoService.getMe().then(r => r.data?.sin_perfil ? null : r.data),
  })

  const plantasDeLaZona = plantas.filter(p =>
    zonaId ? p.zona.id === Number(zonaId) : true
  ).filter(p => p.estado !== 'COSECHADA' && p.estado !== 'MUERTA')

  // Creates Tratamiento(REVISION) for plant disease
  const reportarEnfermedad = useMutation({
    mutationFn: () => {
      if (!plantaId || !descripcion) throw new Error('Completa todos los campos')
      const payload = {
        planta: { id: Number(plantaId) },
        empleado: miEmpleado ? { id: miEmpleado.id } : undefined,
        tipoTratamiento: 'REVISION',
        productoUtilizado: undefined,
        dosis: undefined,
        fechaHora: new Date().toISOString(),
        resultadoObservado: descripcion,
      }
      return tratamientoService.create(payload)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tratamientos'] })
      toast.success('Enfermedad reportada correctamente como revisión')
      setSubmitted(true)
      resetForm()
    },
    onError: (err: any) => toast.error(err?.response?.data?.message ?? 'Error al reportar la novedad'),
  })

  // Creates manual Alerta for zone failure
  const reportarFallaZona = useMutation({
    mutationFn: () => {
      if (!zonaId || !descripcion) throw new Error('Completa todos los campos')
      return alertaService.crearManual({
        zonaId: Number(zonaId),
        tipo: 'FALLA_SISTEMA',
        severidad,
        descripcion,
        empleadoId: miEmpleado?.id,
      })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['alertas'] })
      qc.invalidateQueries({ queryKey: ['alertas-count'] })
      toast.success('Falla de zona reportada como alerta pendiente')
      setSubmitted(true)
      resetForm()
    },
    onError: (err: any) => toast.error(err?.response?.data?.message ?? 'Error al reportar la novedad'),
  })

  const resetForm = () => {
    setZonaId('')
    setPlantaId('')
    setDescripcion('')
    setSeveridad('MEDIA')
  }

  const handleSubmit = () => {
    if (tipo === 'ENFERMEDAD_PLANTA') {
      reportarEnfermedad.mutate()
    } else {
      reportarFallaZona.mutate()
    }
  }

  const isSubmitting = reportarEnfermedad.isPending || reportarFallaZona.isPending
  const canSubmit = descripcion.trim().length > 0 &&
    (tipo === 'FALLA_ZONA' ? !!zonaId : !!plantaId)

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <AlertTriangle className="text-orange-500" size={24} />
          Reportar Novedad
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Reporta una enfermedad en una planta o una falla del sistema en una zona.
        </p>
      </div>

      {submitted && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
          <CheckCircle className="text-green-600" size={20} />
          <p className="text-green-700 text-sm font-medium">
            Novedad reportada correctamente. Puedes reportar otra si es necesario.
          </p>
        </div>
      )}

      {/* Type selector */}
      <div className="bg-white rounded-xl shadow-sm p-5 space-y-4">
        <h2 className="text-sm font-semibold text-gray-700">Tipo de novedad</h2>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => { setTipo('ENFERMEDAD_PLANTA'); setSubmitted(false) }}
            className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
              tipo === 'ENFERMEDAD_PLANTA'
                ? 'border-green-500 bg-green-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <Leaf size={24} className={tipo === 'ENFERMEDAD_PLANTA' ? 'text-green-600' : 'text-gray-400'} />
            <span className="text-sm font-medium text-gray-700">Enfermedad en planta</span>
            <span className="text-xs text-gray-500 text-center">
              Reporta síntomas de enfermedad, plaga o daño en una planta específica
            </span>
          </button>
          <button
            onClick={() => { setTipo('FALLA_ZONA'); setSubmitted(false) }}
            className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
              tipo === 'FALLA_ZONA'
                ? 'border-orange-500 bg-orange-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <AlertTriangle size={24} className={tipo === 'FALLA_ZONA' ? 'text-orange-500' : 'text-gray-400'} />
            <span className="text-sm font-medium text-gray-700">Falla en zona</span>
            <span className="text-xs text-gray-500 text-center">
              Falla de refrigeración, riego, sensores u otro sistema en una zona
            </span>
          </button>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-xl shadow-sm p-5 space-y-4">
        {/* Zone selector — always shown */}
        <div>
          <label className="text-sm font-medium text-gray-700">Zona afectada</label>
          <select
            className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
            value={zonaId}
            onChange={e => { setZonaId(e.target.value); setPlantaId('') }}
          >
            <option value="">— Seleccionar zona —</option>
            {zonas.map(z => (
              <option key={z.id} value={z.id}>{z.nombre}</option>
            ))}
          </select>
        </div>

        {/* Plant selector — only for ENFERMEDAD_PLANTA */}
        {tipo === 'ENFERMEDAD_PLANTA' && (
          <div>
            <label className="text-sm font-medium text-gray-700">Planta afectada</label>
            <select
              className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
              value={plantaId}
              onChange={e => setPlantaId(e.target.value)}
              disabled={!zonaId}
            >
              <option value="">— Seleccionar planta —</option>
              {plantasDeLaZona.map(p => (
                <option key={p.id} value={p.id}>
                  {p.codigo} — {p.tipoPlanta.nombre ?? 'Tipo ' + p.tipoPlanta.id} ({p.estado})
                </option>
              ))}
            </select>
            {zonaId && plantasDeLaZona.length === 0 && (
              <p className="text-xs text-gray-400 mt-1">No hay plantas activas en esta zona</p>
            )}
          </div>
        )}

        {/* Severity — only for FALLA_ZONA */}
        {tipo === 'FALLA_ZONA' && (
          <div>
            <label className="text-sm font-medium text-gray-700">Severidad</label>
            <div className="grid grid-cols-4 gap-2 mt-1">
              {severidades.map(s => (
                <button
                  key={s}
                  onClick={() => setSeveridad(s)}
                  className={`py-2 px-3 rounded-lg text-xs font-medium border transition-all ${
                    severidad === s
                      ? severidadColor[s] + ' ring-2 ring-offset-1 ring-current'
                      : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Description */}
        <div>
          <label className="text-sm font-medium text-gray-700">
            {tipo === 'ENFERMEDAD_PLANTA' ? 'Descripción de los síntomas' : 'Descripción de la falla'}
          </label>
          <textarea
            className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
            rows={4}
            value={descripcion}
            onChange={e => setDescripcion(e.target.value)}
            placeholder={
              tipo === 'ENFERMEDAD_PLANTA'
                ? 'Ej: Manchas amarillas en las hojas, posible hongos. Requiere revisión urgente.'
                : 'Ej: El sistema de refrigeración no está funcionando. La temperatura subió a 35°C.'
            }
          />
          <p className="text-xs text-gray-400 mt-1">{descripcion.length} / 500 caracteres</p>
        </div>

        {/* Reporter info */}
        {miEmpleado && (
          <div className="bg-gray-50 rounded-lg px-3 py-2 text-xs text-gray-600">
            Reportado por: <span className="font-medium">{miEmpleado.nombreCompleto}</span>
          </div>
        )}

        <div className="flex gap-3 pt-2">
          <button
            onClick={handleSubmit}
            disabled={!canSubmit || isSubmitting}
            className={`flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50 ${
              tipo === 'FALLA_ZONA'
                ? 'bg-orange-600 hover:bg-orange-700'
                : 'bg-green-700 hover:bg-green-800'
            }`}
          >
            <AlertTriangle size={14} />
            {isSubmitting ? 'Enviando...' : 'Reportar novedad'}
          </button>
          <button
            onClick={() => { resetForm(); setSubmitted(false) }}
            className="px-4 py-2 rounded-lg text-sm bg-gray-100 text-gray-600 hover:bg-gray-200"
          >
            Limpiar
          </button>
        </div>
      </div>
    </div>
  )
}
