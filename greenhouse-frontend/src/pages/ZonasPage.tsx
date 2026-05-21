/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { zonaService } from '../services/api'
import toast from 'react-hot-toast'
import type { Zona } from '../types'
import { Plus, Pencil, Trash2 } from 'lucide-react'

const emptyZona: Zona = { nombre: '', estado: 'ACTIVA' }

export default function ZonasPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()
  const [form, setForm] = useState<Zona>(emptyZona)
  const [editId, setEditId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)

  const { data: zonas = [], isLoading } = useQuery<Zona[]>({
    queryKey: ['zonas'],
    queryFn: () => zonaService.getAll().then(r => r.data),
  })

  const save = useMutation({
    mutationFn: () => editId ? zonaService.update(editId, form) : zonaService.create(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zonas'] })
      toast.success(editId ? 'Zona actualizada' : 'Zona creada')
      setShowForm(false); setForm(emptyZona); setEditId(null)
    },
    onError: () => toast.error('Error al guardar la zona'),
  })

  const remove = useMutation({
    mutationFn: (id: number) => zonaService.delete(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['zonas'] }); toast.success('Zona eliminada') },
  })

  const startEdit = (z: Zona) => { setForm(z); setEditId(z.id!); setShowForm(true) }

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{t('zona.title')}</h1>
        <button
          onClick={() => { setShowForm(true); setForm(emptyZona); setEditId(null) }}
          className="flex items-center gap-2 bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800 text-sm"
        >
          <Plus size={16} /> {t('zona.nueva')}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="font-semibold text-gray-700 mb-4">{editId ? t('common.edit') : t('zona.nueva')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-600">{t('zona.nombre')}</label>
              <input className="w-full border rounded-lg px-3 py-2 mt-1 text-sm" value={form.nombre}
                onChange={e => setForm({ ...form, nombre: e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('zona.estado')}</label>
              <select className="w-full border rounded-lg px-3 py-2 mt-1 text-sm" value={form.estado}
                onChange={e => setForm({ ...form, estado: e.target.value as Zona['estado'] })}>
                <option value="ACTIVA">{t('zona.ACTIVA')}</option>
                <option value="EN_MANTENIMIENTO">{t('zona.EN_MANTENIMIENTO')}</option>
                <option value="INACTIVA">{t('zona.INACTIVA')}</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('zona.dimension')}</label>
              <input type="number" className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.dimensionM2 ?? ''} onChange={e => setForm({ ...form, dimensionM2: +e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('zona.ubicacion')}</label>
              <input className="w-full border rounded-lg px-3 py-2 mt-1 text-sm" value={form.ubicacion ?? ''}
                onChange={e => setForm({ ...form, ubicacion: e.target.value })} />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button onClick={() => save.mutate()} className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-800">
              {t('common.save')}
            </button>
            <button onClick={() => setShowForm(false)} className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-200">
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

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
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">{t('common.noData')}</td></tr>
            )}
            {zonas.map((z) => (
              <tr key={z.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{z.nombre}</td>
                <td className="px-4 py-3">{z.dimensionM2 ? `${z.dimensionM2} m²` : '-'}</td>
                <td className="px-4 py-3">{z.capacidadMaxPlantas ?? '-'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${z.estado === 'ACTIVA' ? 'bg-green-100 text-green-800' : z.estado === 'EN_MANTENIMIENTO' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-600'}`}>
                    {t(`zona.${z.estado}`)}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">{z.ubicacion ?? '-'}</td>
                <td className="px-4 py-3 flex gap-2">
                  <button onClick={() => startEdit(z)} className="text-blue-600 hover:text-blue-800"><Pencil size={15} /></button>
                  <button onClick={() => remove.mutate(z.id!)} className="text-red-500 hover:text-red-700"><Trash2 size={15} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
