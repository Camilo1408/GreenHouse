/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { plantaService, zonaService, tipoPlantaService } from '../services/api'
import toast from 'react-hot-toast'
import type { Planta, Zona, TipoPlanta } from '../types'
import { Plus, Pencil, Trash2, Leaf } from 'lucide-react'

type PlantaEstado = Planta['estado']

const estadoColor: Record<PlantaEstado, string> = {
  SEMBRADA: 'bg-blue-100 text-blue-800',
  EN_CRECIMIENTO: 'bg-green-100 text-green-800',
  LISTA_PARA_COSECHAR: 'bg-yellow-100 text-yellow-800',
  COSECHADA: 'bg-gray-100 text-gray-600',
  MUERTA: 'bg-red-100 text-red-800',
}

/** Calcula días restantes hasta la cosecha estimada */
function calcDiasRestantes(fechaSiembra: string, cicloDias: number): number {
  const siembra = new Date(fechaSiembra + 'T00:00:00')
  const cosecha = new Date(siembra.getTime() + cicloDias * 24 * 60 * 60 * 1000)
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  return Math.round((cosecha.getTime() - hoy.getTime()) / (24 * 60 * 60 * 1000))
}

function fechaCosechaEstimada(fechaSiembra: string, cicloDias: number): string {
  const siembra = new Date(fechaSiembra + 'T00:00:00')
  const cosecha = new Date(siembra.getTime() + cicloDias * 24 * 60 * 60 * 1000)
  return cosecha.toISOString().split('T')[0]
}

const emptyForm = {
  codigo: '',
  tipoPlantaId: '',
  zonaId: '',
  fechaSiembra: new Date().toISOString().split('T')[0],
  estado: 'SEMBRADA' as PlantaEstado,
  observaciones: '',
}

export default function PlantasPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()
  const [form, setForm] = useState(emptyForm)
  const [editId, setEditId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)

  const { data: plantas = [], isLoading } = useQuery<Planta[]>({
    queryKey: ['plantas'],
    queryFn: () => plantaService.getAll().then(r => r.data),
  })

  const { data: zonas = [] } = useQuery<Zona[]>({
    queryKey: ['zonas'],
    queryFn: () => zonaService.getAll().then(r => r.data),
  })

  const { data: tipos = [] } = useQuery<TipoPlanta[]>({
    queryKey: ['tiposPlanta'],
    queryFn: () => tipoPlantaService.getAll().then(r => r.data),
  })

  const save = useMutation({
    mutationFn: () => {
      const payload = {
        codigo: form.codigo,
        tipoPlanta: { id: Number(form.tipoPlantaId) },
        zona: { id: Number(form.zonaId) },
        fechaSiembra: form.fechaSiembra,
        estado: form.estado,
        observaciones: form.observaciones || undefined,
      }
      return editId
        ? plantaService.update(editId, payload)
        : plantaService.create(payload)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['plantas'] })
      toast.success(editId ? 'Planta actualizada' : 'Planta registrada')
      setShowForm(false)
      setForm(emptyForm)
      setEditId(null)
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.message ?? 'Error al guardar la planta')
    },
  })

  const remove = useMutation({
    mutationFn: (id: number) => plantaService.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['plantas'] })
      toast.success('Planta eliminada')
    },
    onError: () => toast.error('Error al eliminar la planta'),
  })

  const startEdit = (p: Planta) => {
    setForm({
      codigo: p.codigo,
      tipoPlantaId: String(p.tipoPlanta.id),
      zonaId: String(p.zona.id),
      fechaSiembra: p.fechaSiembra,
      estado: p.estado,
      observaciones: p.observaciones ?? '',
    })
    setEditId(p.id!)
    setShowForm(true)
  }

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Leaf className="text-green-600" size={24} />
          {t('planta.title')}
        </h1>
        <button
          onClick={() => { setShowForm(true); setForm(emptyForm); setEditId(null) }}
          className="flex items-center gap-2 bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800 text-sm"
        >
          <Plus size={16} /> {t('planta.nueva')}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6 border border-green-100">
          <h2 className="font-semibold text-gray-700 mb-4">
            {editId ? t('common.edit') : t('planta.nueva')}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-gray-600">{t('planta.codigo')}</label>
              <input
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.codigo}
                onChange={e => setForm({ ...form, codigo: e.target.value })}
                placeholder="PL-001"
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('planta.tipo')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.tipoPlantaId}
                onChange={e => setForm({ ...form, tipoPlantaId: e.target.value })}
              >
                <option value="">— Seleccionar —</option>
                {tipos.map(tp => (
                  <option key={tp.id} value={tp.id}>
                    {tp.nombre} ({tp.cicloDias} días)
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('planta.zona')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.zonaId}
                onChange={e => setForm({ ...form, zonaId: e.target.value })}
              >
                <option value="">— Seleccionar —</option>
                {zonas.map(z => (
                  <option key={z.id} value={z.id}>{z.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('planta.siembra')}</label>
              <input
                type="date"
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.fechaSiembra}
                onChange={e => setForm({ ...form, fechaSiembra: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('planta.estado')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.estado}
                onChange={e => setForm({ ...form, estado: e.target.value as PlantaEstado })}
              >
                <option value="SEMBRADA">{t('planta.SEMBRADA')}</option>
                <option value="EN_CRECIMIENTO">{t('planta.EN_CRECIMIENTO')}</option>
                <option value="LISTA_PARA_COSECHAR">{t('planta.LISTA_PARA_COSECHAR')}</option>
                <option value="COSECHADA">{t('planta.COSECHADA')}</option>
                <option value="MUERTA">{t('planta.MUERTA')}</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('planta.observaciones')}</label>
              <input
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.observaciones}
                onChange={e => setForm({ ...form, observaciones: e.target.value })}
                placeholder="Observaciones opcionales"
              />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => save.mutate()}
              disabled={!form.codigo || !form.tipoPlantaId || !form.zonaId}
              className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-800 disabled:opacity-50"
            >
              {t('common.save')}
            </button>
            <button
              onClick={() => { setShowForm(false); setForm(emptyForm); setEditId(null) }}
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
              <th className="px-4 py-3 text-left">{t('planta.codigo')}</th>
              <th className="px-4 py-3 text-left">{t('planta.tipo')}</th>
              <th className="px-4 py-3 text-left">{t('planta.zona')}</th>
              <th className="px-4 py-3 text-left">{t('planta.siembra')}</th>
              <th className="px-4 py-3 text-left">{t('planta.cosechaEst')}</th>
              <th className="px-4 py-3 text-left">{t('planta.estado')}</th>
              <th className="px-4 py-3 text-left">{t('common.actions')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {plantas.length === 0 && (
              <tr>
                <td colSpan={7} className="text-center py-8 text-gray-400">
                  {t('common.noData')}
                </td>
              </tr>
            )}
            {plantas.map((p) => {
              const cicloDias = p.tipoPlanta.cicloDias ?? 90
              const diasRestantes = calcDiasRestantes(p.fechaSiembra, cicloDias)
              const fechaCosecha = fechaCosechaEstimada(p.fechaSiembra, cicloDias)
              const esProximo = diasRestantes >= 0 && diasRestantes <= 7
              const vencida = diasRestantes < 0

              return (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono font-medium">{p.codigo}</td>
                  <td className="px-4 py-3 text-gray-600">{p.tipoPlanta.nombre ?? `ID ${p.tipoPlanta.id}`}</td>
                  <td className="px-4 py-3 text-gray-600">{p.zona.nombre ?? `Zona ${p.zona.id}`}</td>
                  <td className="px-4 py-3 text-gray-500">{p.fechaSiembra}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-col gap-1">
                      <span className="text-gray-600">{fechaCosecha}</span>
                      {p.estado !== 'COSECHADA' && p.estado !== 'MUERTA' && (
                        esProximo ? (
                          <span className="inline-flex items-center gap-1 bg-orange-100 text-orange-700 px-2 py-0.5 rounded text-xs font-medium">
                            🌾 {diasRestantes === 0 ? '¡Hoy!' : `${diasRestantes} ${t('planta.diasRestantes')}`}
                          </span>
                        ) : vencida ? (
                          <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-medium">
                            ⚠ {t('planta.vencida')} ({Math.abs(diasRestantes)}d)
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400">{diasRestantes}d</span>
                        )
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${estadoColor[p.estado]}`}>
                      {t(`planta.${p.estado}`)}
                    </span>
                  </td>
                  <td className="px-4 py-3 flex gap-2">
                    <button
                      onClick={() => startEdit(p)}
                      className="text-blue-600 hover:text-blue-800"
                      title={t('common.edit')}
                    >
                      <Pencil size={15} />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm(`¿Eliminar planta ${p.codigo}?`)) remove.mutate(p.id!)
                      }}
                      className="text-red-500 hover:text-red-700"
                      title={t('common.delete')}
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
