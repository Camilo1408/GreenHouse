/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { zonaService, sensorService } from '../services/api'
import toast from 'react-hot-toast'
import type { Zona, Sensor } from '../types'
import {
  Plus, Pencil, Trash2, LayoutDashboard,
  Thermometer, Droplets, Wind, Sun, FlaskConical, X, Activity
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

type TipoSensor = Sensor['tipoSensor']

interface SensorRow {
  tipoSensor: TipoSensor
  codigo: string
  umbralMin: number | ''
  umbralMax: number | ''
}

const TIPO_DEFAULTS: Record<TipoSensor, { min: number; max: number; unit: string }> = {
  TEMPERATURA: { min: 15, max: 30,    unit: '°C'  },
  HUMEDAD:     { min: 40, max: 80,    unit: '%'   },
  CO2:         { min: 400, max: 1500, unit: 'ppm' },
  PH:          { min: 5.5, max: 7.0,  unit: 'pH'  },
  LUZ:         { min: 1000, max: 50000, unit: 'lux' },
}

const TIPO_ICONS: Record<TipoSensor, React.ReactNode> = {
  TEMPERATURA: <Thermometer size={13} />,
  HUMEDAD:     <Droplets size={13} />,
  CO2:         <Wind size={13} />,
  PH:          <FlaskConical size={13} />,
  LUZ:         <Sun size={13} />,
}

const emptyZona: Zona = { nombre: '', estado: 'ACTIVA' }

const newSensorRow = (tipo: TipoSensor = 'TEMPERATURA'): SensorRow => ({
  tipoSensor: tipo,
  codigo: '',
  umbralMin: TIPO_DEFAULTS[tipo].min,
  umbralMax: TIPO_DEFAULTS[tipo].max,
})

export default function ZonasPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()
  const navigate = useNavigate()
  const { canWrite, isAdmin } = useAuth()

  const [form, setForm] = useState<Zona>(emptyZona)
  const [editId, setEditId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [sensorRows, setSensorRows] = useState<SensorRow[]>([])

  /* ── data ── */
  const { data: zonas = [], isLoading } = useQuery<Zona[]>({
    queryKey: ['zonas'],
    queryFn: () => zonaService.getAll().then(r => r.data),
  })

  // Existing sensors shown when editing a zone
  const { data: sensoresExistentes = [] } = useQuery<Sensor[]>({
    queryKey: ['sensores-zona', editId],
    queryFn: () => sensorService.getByZona(editId!).then(r => r.data),
    enabled: !!editId,
  })

  /* ── mutations ── */
  const save = useMutation({
    mutationFn: async () => {
      // 1. Create/update the zone
      const resp = editId
        ? await zonaService.update(editId, form)
        : await zonaService.create(form)
      const zonaId: number = resp.data.id

      // 2. Create each sensor row that has a código
      const toCreate = sensorRows.filter(s => s.codigo.trim() !== '')
      for (const row of toCreate) {
        await sensorService.create({
          codigo: row.codigo.trim(),
          tipoSensor: row.tipoSensor,
          zona: { id: zonaId },
          estado: 'ACTIVO',
          fechaInstalacion: new Date().toISOString().split('T')[0],
          umbralMin: row.umbralMin !== '' ? Number(row.umbralMin) : undefined,
          umbralMax: row.umbralMax !== '' ? Number(row.umbralMax) : undefined,
        })
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zonas'] })
      qc.invalidateQueries({ queryKey: ['sensores'] })
      qc.invalidateQueries({ queryKey: ['sensores-zona', editId] })
      toast.success(editId ? t('zona.actualizada') : t('zona.creada'))
      closeForm()
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.message ?? t('zona.errorGuardar')),
  })

  const remove = useMutation({
    mutationFn: (id: number) => zonaService.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zonas'] })
      toast.success(t('zona.eliminada'))
    },
  })

  /* ── helpers ── */
  const startEdit = (z: Zona) => {
    setForm(z)
    setEditId(z.id!)
    setSensorRows([])
    setShowForm(true)
  }

  const closeForm = () => {
    setShowForm(false)
    setForm(emptyZona)
    setEditId(null)
    setSensorRows([])
  }

  const addSensorRow = () =>
    setSensorRows(prev => [...prev, newSensorRow()])

  const removeSensorRow = (i: number) =>
    setSensorRows(prev => prev.filter((_, idx) => idx !== i))

  const updateRow = (i: number, field: keyof SensorRow, value: string | number) => {
    setSensorRows(prev => {
      const next = [...prev]
      if (field === 'tipoSensor') {
        const tipo = value as TipoSensor
        next[i] = {
          ...next[i],
          tipoSensor: tipo,
          umbralMin: TIPO_DEFAULTS[tipo].min,
          umbralMax: TIPO_DEFAULTS[tipo].max,
        }
      } else {
        next[i] = { ...next[i], [field]: value }
      }
      return next
    })
  }

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      {/* ── Header ── */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{t('zona.title')}</h1>
        {canWrite && (
          <button
            onClick={() => { setShowForm(true); setForm(emptyZona); setEditId(null); setSensorRows([]) }}
            className="flex items-center gap-2 bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800 text-sm"
          >
            <Plus size={16} /> {t('zona.nueva')}
          </button>
        )}
      </div>

      {/* ── Form ── */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6 border border-green-100">
          <h2 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            {editId ? <Pencil size={16} /> : <Plus size={16} />}
            {editId ? t('common.edit') : t('zona.nueva')}
          </h2>

          {/* Zone fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-600">{t('zona.nombre')} *</label>
              <input
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.nombre}
                onChange={e => setForm({ ...form, nombre: e.target.value })}
                placeholder="Ej: Zona A - Tomates"
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('zona.estado')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.estado}
                onChange={e => setForm({ ...form, estado: e.target.value as Zona['estado'] })}
              >
                <option value="ACTIVA">{t('zona.ACTIVA')}</option>
                <option value="EN_MANTENIMIENTO">{t('zona.EN_MANTENIMIENTO')}</option>
                <option value="INACTIVA">{t('zona.INACTIVA')}</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('zona.dimension')}</label>
              <input
                type="number"
                min="0"
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.dimensionM2 ?? ''}
                placeholder="m²"
                onChange={e => setForm({ ...form, dimensionM2: +e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('zona.capacidad')}</label>
              <input
                type="number"
                min="1"
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.capacidadMaxPlantas ?? ''}
                placeholder="Ej: 200"
                onChange={e => setForm({ ...form, capacidadMaxPlantas: +e.target.value })}
              />
            </div>
            <div className="md:col-span-2">
              <label className="text-sm text-gray-600">{t('zona.ubicacion')}</label>
              <input
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.ubicacion ?? ''}
                placeholder="Ej: Sector Norte, Invernadero 1"
                onChange={e => setForm({ ...form, ubicacion: e.target.value })}
              />
            </div>
          </div>

          {/* Existing sensors badge row (edit mode only) */}
          {editId && sensoresExistentes.length > 0 && (
            <div className="mt-5">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                {t('zona.sensoresActuales')}
              </p>
              <div className="flex flex-wrap gap-2">
                {sensoresExistentes.map(s => (
                  <span
                    key={s.id}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 text-blue-700 text-xs rounded-full border border-blue-100"
                  >
                    {TIPO_ICONS[s.tipoSensor]}
                    <span className="font-mono">{s.codigo}</span>
                    <span className="text-blue-400">·</span>
                    {t(`sensor.${s.tipoSensor}`)}
                    {s.umbralMin != null && s.umbralMax != null && (
                      <span className="text-blue-400 ml-1">
                        {s.umbralMin}–{s.umbralMax} {TIPO_DEFAULTS[s.tipoSensor].unit}
                      </span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* ── Sensor section ── */}
          <div className="mt-5 pt-5 border-t border-gray-100">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Activity size={15} className="text-green-600" />
                <p className="text-sm font-semibold text-gray-700">{t('zona.sensores')}</p>
                {sensorRows.length > 0 && (
                  <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full font-medium">
                    {sensorRows.length}
                  </span>
                )}
              </div>
              <button
                type="button"
                onClick={addSensorRow}
                className="flex items-center gap-1 text-xs text-green-700 hover:text-green-900 font-medium border border-green-300 rounded-lg px-2.5 py-1 hover:bg-green-50 transition-colors"
              >
                <Plus size={13} /> {t('zona.agregarSensor')}
              </button>
            </div>

            {sensorRows.length === 0 && (
              <p className="text-xs text-gray-400 italic py-1">{t('zona.sinSensores')}</p>
            )}

            <div className="space-y-2">
              {sensorRows.map((row, i) => {
                const defs = TIPO_DEFAULTS[row.tipoSensor]
                return (
                  <div
                    key={i}
                    className="grid grid-cols-12 gap-2 items-end p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    {/* Tipo */}
                    <div className="col-span-12 sm:col-span-3">
                      <label className="text-xs text-gray-500">{t('sensor.tipo')}</label>
                      <select
                        className="w-full border rounded-md px-2 py-1.5 text-xs mt-0.5 bg-white"
                        value={row.tipoSensor}
                        onChange={e => updateRow(i, 'tipoSensor', e.target.value)}
                      >
                        {(Object.keys(TIPO_DEFAULTS) as TipoSensor[]).map(tp => (
                          <option key={tp} value={tp}>
                            {t(`sensor.${tp}`)}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Código */}
                    <div className="col-span-12 sm:col-span-3">
                      <label className="text-xs text-gray-500">{t('sensor.codigo')}</label>
                      <input
                        className="w-full border rounded-md px-2 py-1.5 text-xs mt-0.5 font-mono"
                        value={row.codigo}
                        placeholder={`SENS-${row.tipoSensor.slice(0, 2)}-01`}
                        onChange={e => updateRow(i, 'codigo', e.target.value)}
                      />
                    </div>

                    {/* Umbral mín */}
                    <div className="col-span-5 sm:col-span-2">
                      <label className="text-xs text-gray-500">
                        {t('sensor.umbralMin')} <span className="text-gray-400">({defs.unit})</span>
                      </label>
                      <input
                        type="number"
                        className="w-full border rounded-md px-2 py-1.5 text-xs mt-0.5"
                        value={row.umbralMin}
                        onChange={e => updateRow(i, 'umbralMin', e.target.value)}
                      />
                    </div>

                    {/* Umbral máx */}
                    <div className="col-span-5 sm:col-span-2">
                      <label className="text-xs text-gray-500">
                        {t('sensor.umbralMax')} <span className="text-gray-400">({defs.unit})</span>
                      </label>
                      <input
                        type="number"
                        className="w-full border rounded-md px-2 py-1.5 text-xs mt-0.5"
                        value={row.umbralMax}
                        onChange={e => updateRow(i, 'umbralMax', e.target.value)}
                      />
                    </div>

                    {/* Remove button */}
                    <div className="col-span-2 sm:col-span-2 flex justify-end items-end pb-0.5">
                      <button
                        type="button"
                        onClick={() => removeSensorRow(i)}
                        className="p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                        title={t('common.delete')}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3 mt-5">
            <button
              onClick={() => save.mutate()}
              disabled={save.isPending || !form.nombre.trim()}
              className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-800 disabled:opacity-50 flex items-center gap-2"
            >
              {save.isPending && <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {save.isPending ? t('common.loading') : t('common.save')}
            </button>
            <button
              onClick={closeForm}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-200"
            >
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* ── Table ── */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              <th className="px-4 py-3 text-left">{t('zona.nombre')}</th>
              <th className="px-4 py-3 text-left">{t('zona.dimension')}</th>
              <th className="px-4 py-3 text-left">{t('zona.capacidad')}</th>
              <th className="px-4 py-3 text-left">{t('zona.estado')}</th>
              <th className="px-4 py-3 text-left">{t('zona.ubicacion')}</th>
              <th className="px-4 py-3 text-left">{t('common.actions')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {zonas.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-400">
                  {t('common.noData')}
                </td>
              </tr>
            )}
            {zonas.map(z => (
              <tr key={z.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{z.nombre}</td>
                <td className="px-4 py-3">{z.dimensionM2 ? `${z.dimensionM2} m²` : '—'}</td>
                <td className="px-4 py-3">{z.capacidadMaxPlantas ?? '—'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    z.estado === 'ACTIVA'
                      ? 'bg-green-100 text-green-800'
                      : z.estado === 'EN_MANTENIMIENTO'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {t(`zona.${z.estado}`)}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">{z.ubicacion ?? '—'}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/zonas/${z.id}`)}
                      className="text-green-600 hover:text-green-800"
                      title={t('zona.dashboard')}
                    >
                      <LayoutDashboard size={15} />
                    </button>
                    {canWrite && (
                      <button
                        onClick={() => startEdit(z)}
                        className="text-blue-600 hover:text-blue-800"
                        title={t('common.edit')}
                      >
                        <Pencil size={15} />
                      </button>
                    )}
                    {isAdmin && (
                      <button
                        onClick={() => remove.mutate(z.id!)}
                        className="text-red-500 hover:text-red-700"
                        title={t('common.delete')}
                      >
                        <Trash2 size={15} />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
