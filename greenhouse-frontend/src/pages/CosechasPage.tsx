/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { cosechaService, plantaService, empleadoService } from '../services/api'
import toast from 'react-hot-toast'
import type { Cosecha, Planta, Empleado } from '../types'
import { Plus, Wheat } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

type Calidad = Cosecha['calidad']
type Destino = Cosecha['destino']

const calidadColor: Record<Calidad, string> = {
  A: 'bg-green-100 text-green-800',
  B: 'bg-yellow-100 text-yellow-800',
  C: 'bg-red-100 text-red-800',
}

const emptyForm = {
  plantaId: '',
  empleadoId: '',
  fechaCosecha: new Date().toISOString().split('T')[0],
  pesoKg: '',
  calidad: 'A' as Calidad,
  destino: 'VENTA' as Destino,
  observaciones: '',
}

export default function CosechasPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()
  const { isAdmin } = useAuth()
  const [form, setForm] = useState(emptyForm)
  const [showForm, setShowForm] = useState(false)

  const { data: cosechas = [], isLoading } = useQuery<Cosecha[]>({
    queryKey: ['cosechas'],
    queryFn: () => cosechaService.getAll().then(r => r.data),
  })

  const { data: plantas = [] } = useQuery<Planta[]>({
    queryKey: ['plantas'],
    queryFn: () => plantaService.getAll().then(r => r.data),
  })

  // Only admins can pick from the full employee list
  const { data: empleados = [] } = useQuery<Empleado[]>({
    queryKey: ['empleados'],
    queryFn: () => empleadoService.getAll().then(r => r.data),
    enabled: isAdmin,
  })

  // Non-admins use their own employee record to auto-populate
  const { data: miEmpleado } = useQuery<Empleado | null>({
    queryKey: ['empleados-me'],
    queryFn: () => empleadoService.getMe().then(r => r.data?.sin_perfil ? null : r.data),
    enabled: !isAdmin,
  })

  const plantasActivas = plantas.filter(
    p => p.estado === 'LISTA_PARA_COSECHAR' || p.estado === 'EN_CRECIMIENTO' || p.estado === 'SEMBRADA'
  )

  const registrar = useMutation({
    mutationFn: () => {
      // Admins pick from dropdown; others use their own employee record
      const empleadoId = isAdmin
        ? Number(form.empleadoId)
        : (miEmpleado?.id ?? Number(form.empleadoId))
      const payload = {
        planta: { id: Number(form.plantaId) },
        empleado: { id: empleadoId },
        fechaCosecha: form.fechaCosecha,
        pesoKg: Number(form.pesoKg),
        calidad: form.calidad,
        destino: form.destino,
        observaciones: form.observaciones || undefined,
      }
      return cosechaService.registrar(payload)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['cosechas'] })
      qc.invalidateQueries({ queryKey: ['plantas'] })
      toast.success(t('cosecha.registrada'))
      setShowForm(false)
      setForm(emptyForm)
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.message ?? t('cosecha.errorRegistrar'))
    },
  })

  // Stats
  const totalKg = cosechas.reduce((sum, c) => sum + (c.pesoKg ?? 0), 0)
  const mesActual = new Date().getMonth()
  const cosechasMes = cosechas.filter(c => new Date(c.fechaCosecha).getMonth() === mesActual)
  const kgMes = cosechasMes.reduce((sum, c) => sum + (c.pesoKg ?? 0), 0)

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Wheat className="text-yellow-600" size={24} />
          {t('cosecha.title')}
        </h1>
        <button
          onClick={() => { setShowForm(true); setForm(emptyForm) }}
          className="flex items-center gap-2 bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800 text-sm"
        >
          <Plus size={16} /> {t('cosecha.nueva')}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-yellow-400">
          <p className="text-xs text-gray-500 uppercase">{t('cosecha.totalCosechado')}</p>
          <p className="text-2xl font-bold text-gray-800 mt-1">{totalKg.toFixed(1)} kg</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-green-400">
          <p className="text-xs text-gray-500 uppercase">{t('cosecha.cosechasMes')}</p>
          <p className="text-2xl font-bold text-gray-800 mt-1">{cosechasMes.length}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-blue-400">
          <p className="text-xs text-gray-500 uppercase">{t('cosecha.kgMes')}</p>
          <p className="text-2xl font-bold text-gray-800 mt-1">{kgMes.toFixed(1)} kg</p>
        </div>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6 border border-yellow-100">
          <h2 className="font-semibold text-gray-700 mb-4">{t('cosecha.nueva')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.planta')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.plantaId}
                onChange={e => setForm({ ...form, plantaId: e.target.value })}
              >
                <option value="">{t('cosecha.seleccionarPlanta')}</option>
                {plantasActivas.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.codigo} — {p.tipoPlanta.nombre ?? 'Tipo ' + p.tipoPlanta.id} ({p.estado.replace('_', ' ')})
                  </option>
                ))}
              </select>
            </div>
            {isAdmin ? (
              <div>
                <label className="text-sm text-gray-600">{t('cosecha.empleado')}</label>
                <select
                  className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                  value={form.empleadoId}
                  onChange={e => setForm({ ...form, empleadoId: e.target.value })}
                >
                  <option value="">— Seleccionar empleado —</option>
                  {empleados.filter(e => e.estado === 'ACTIVO').map(e => (
                    <option key={e.id} value={e.id}>{e.nombreCompleto}</option>
                  ))}
                </select>
              </div>
            ) : (
              <div>
                <label className="text-sm text-gray-600">{t('cosecha.empleado')}</label>
                <input
                  readOnly
                  className="w-full border rounded-lg px-3 py-2 mt-1 text-sm bg-gray-50 text-gray-600"
                  value={miEmpleado?.nombreCompleto ?? 'Sin perfil de empleado'}
                />
              </div>
            )}
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.fecha')}</label>
              <input
                type="date"
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.fechaCosecha}
                onChange={e => setForm({ ...form, fechaCosecha: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.peso')}</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.pesoKg}
                onChange={e => setForm({ ...form, pesoKg: e.target.value })}
                placeholder="0.00"
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.calidad')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.calidad}
                onChange={e => setForm({ ...form, calidad: e.target.value as Calidad })}
              >
                <option value="A">A — Premium</option>
                <option value="B">B — Estándar</option>
                <option value="C">C — Descarte</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.destino')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.destino}
                onChange={e => setForm({ ...form, destino: e.target.value as Destino })}
              >
                <option value="VENTA">{t('cosecha.VENTA')}</option>
                <option value="CONSUMO_INTERNO">{t('cosecha.CONSUMO_INTERNO')}</option>
                <option value="DESCARTE">{t('cosecha.DESCARTE')}</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="text-sm text-gray-600">{t('cosecha.observaciones')}</label>
              <textarea
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                rows={2}
                value={form.observaciones}
                onChange={e => setForm({ ...form, observaciones: e.target.value })}
                placeholder="Observaciones sobre la cosecha..."
              />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => registrar.mutate()}
              disabled={!form.plantaId || (isAdmin ? !form.empleadoId : !miEmpleado) || !form.pesoKg}
              className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-800 disabled:opacity-50"
            >
              {t('common.save')}
            </button>
            <button
              onClick={() => { setShowForm(false); setForm(emptyForm) }}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-200"
            >
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              <th className="px-4 py-3 text-left">{t('cosecha.fecha')}</th>
              <th className="px-4 py-3 text-left">{t('cosecha.planta')}</th>
              <th className="px-4 py-3 text-left">{t('cosecha.empleado')}</th>
              <th className="px-4 py-3 text-left">{t('cosecha.peso')}</th>
              <th className="px-4 py-3 text-left">{t('cosecha.calidad')}</th>
              <th className="px-4 py-3 text-left">{t('cosecha.destino')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {cosechas.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-400">
                  {t('common.noData')}
                </td>
              </tr>
            )}
            {cosechas.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">{c.fechaCosecha}</td>
                <td className="px-4 py-3 font-mono text-xs">
                  {c.planta.codigo ?? `Planta ${c.planta.id}`}
                  {c.planta.tipoPlanta?.nombre && (
                    <span className="text-gray-400 ml-1">({c.planta.tipoPlanta.nombre})</span>
                  )}
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {c.empleado.nombreCompleto ?? `Empleado ${c.empleado.id}`}
                </td>
                <td className="px-4 py-3 font-medium">{c.pesoKg} kg</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${calidadColor[c.calidad]}`}>
                    {c.calidad}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">{t(`cosecha.${c.destino}`)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
