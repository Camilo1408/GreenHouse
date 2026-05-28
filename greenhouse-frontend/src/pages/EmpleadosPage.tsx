/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { empleadoService } from '../services/api'
import toast from 'react-hot-toast'
import type { Empleado } from '../types'
import { Plus, Pencil, Trash2, Users } from 'lucide-react'

type Rol = Empleado['rol']
type Estado = Empleado['estado']

const rolColor: Record<Rol, string> = {
  ADMINISTRADOR: 'bg-purple-100 text-purple-800',
  SUPERVISOR: 'bg-blue-100 text-blue-800',
  EMPLEADO: 'bg-gray-100 text-gray-700',
}

const emptyForm = {
  nombreCompleto: '',
  email: '',
  password: '',
  rol: 'EMPLEADO' as Rol,
  telefono: '',
  estado: 'ACTIVO' as Estado,
}

export default function EmpleadosPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()
  const [form, setForm] = useState(emptyForm)
  const [editId, setEditId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)

  const { data: empleados = [], isLoading } = useQuery<Empleado[]>({
    queryKey: ['empleados'],
    queryFn: () => empleadoService.getAll().then(r => r.data),
  })

  const save = useMutation({
    mutationFn: () => {
      const payload: any = {
        nombreCompleto: form.nombreCompleto,
        email: form.email,
        rol: form.rol,
        telefono: form.telefono || undefined,
        estado: form.estado,
      }
      if (!editId && form.password) {
        payload.passwordHash = form.password
      }
      return editId
        ? empleadoService.update(editId, payload)
        : empleadoService.create(payload)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['empleados'] })
      toast.success(editId ? 'Empleado actualizado' : 'Empleado registrado')
      setShowForm(false)
      setForm(emptyForm)
      setEditId(null)
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.message ?? 'Error al guardar el empleado')
    },
  })

  const remove = useMutation({
    mutationFn: (id: number) => empleadoService.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['empleados'] })
      toast.success(t('empleado.eliminado'))
    },
    onError: () => toast.error(t('empleado.errorEliminar')),
  })

  const startEdit = (e: Empleado) => {
    setForm({
      nombreCompleto: e.nombreCompleto,
      email: e.email,
      password: '',
      rol: e.rol,
      telefono: e.telefono ?? '',
      estado: e.estado,
    })
    setEditId(e.id!)
    setShowForm(true)
  }

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Users className="text-blue-600" size={24} />
          {t('nav.empleados')}
        </h1>
        <button
          onClick={() => { setShowForm(true); setForm(emptyForm); setEditId(null) }}
          className="flex items-center gap-2 bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800 text-sm"
        >
          <Plus size={16} /> {t('empleado.nuevo')}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6 border border-blue-50">
          <h2 className="font-semibold text-gray-700 mb-4">
            {editId ? t('common.edit') : t('empleado.nuevo')}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-gray-600">{t('empleado.nombre')}</label>
              <input
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.nombreCompleto}
                onChange={e => setForm({ ...form, nombreCompleto: e.target.value })}
                placeholder={t('empleado.nombre')}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('empleado.email')}</label>
              <input
                type="email"
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                placeholder="correo@ejemplo.com"
                disabled={!!editId}
              />
            </div>
            {!editId && (
              <div>
                <label className="text-sm text-gray-600">{t('empleado.password')}</label>
                <input
                  type="password"
                  className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                  value={form.password}
                  onChange={e => setForm({ ...form, password: e.target.value })}
                  placeholder={t('empleado.passwordPlaceholder')}
                />
              </div>
            )}
            <div>
              <label className="text-sm text-gray-600">{t('empleado.rol')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.rol}
                onChange={e => setForm({ ...form, rol: e.target.value as Rol })}
              >
                <option value="ADMINISTRADOR">{t('empleado.ADMINISTRADOR')}</option>
                <option value="SUPERVISOR">{t('empleado.SUPERVISOR')}</option>
                <option value="EMPLEADO">{t('empleado.EMPLEADO')}</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('empleado.telefono')}</label>
              <input
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.telefono}
                onChange={e => setForm({ ...form, telefono: e.target.value })}
                placeholder="+57 300 0000000"
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('common.status')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.estado}
                onChange={e => setForm({ ...form, estado: e.target.value as Estado })}
              >
                <option value="ACTIVO">{t('empleado.ACTIVO')}</option>
                <option value="INACTIVO">{t('empleado.INACTIVO')}</option>
              </select>
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => save.mutate()}
              disabled={!form.nombreCompleto || !form.email}
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
              <th className="px-4 py-3 text-left">{t('empleado.nombre')}</th>
              <th className="px-4 py-3 text-left">{t('empleado.email')}</th>
              <th className="px-4 py-3 text-left">{t('empleado.telefono')}</th>
              <th className="px-4 py-3 text-left">{t('empleado.rol')}</th>
              <th className="px-4 py-3 text-left">{t('common.status')}</th>
              <th className="px-4 py-3 text-left">{t('common.actions')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {empleados.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-400">
                  {t('common.noData')}
                </td>
              </tr>
            )}
            {empleados.map((e) => (
              <tr key={e.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{e.nombreCompleto}</td>
                <td className="px-4 py-3 text-gray-500">{e.email}</td>
                <td className="px-4 py-3 text-gray-500">{e.telefono ?? '—'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${rolColor[e.rol]}`}>
                    {e.rol}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    e.estado === 'ACTIVO'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {t(`empleado.${e.estado}`)}
                  </span>
                </td>
                <td className="px-4 py-3 flex gap-2">
                  <button
                    onClick={() => startEdit(e)}
                    className="text-blue-600 hover:text-blue-800"
                    title={t('common.edit')}
                  >
                    <Pencil size={15} />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm(t('empleado.confirmarEliminar', { nombre: e.nombreCompleto }))) remove.mutate(e.id!)
                    }}
                    className="text-red-500 hover:text-red-700"
                    title={t('common.delete')}
                  >
                    <Trash2 size={15} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
