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
import { Plus, Pencil, Trash2, Leaf, PlusCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

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
  const { canWrite, isAdmin } = useAuth()
  const [form, setForm] = useState(emptyForm)
  const [editId, setEditId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)

  // Sub-form para crear nuevo tipo de planta inline
  const [showNuevoTipo, setShowNuevoTipo] = useState(false)
  const emptyNuevoTipo = { nombre: '', cicloDias: '', descripcion: '', temperaturaMin: '15', temperaturaMax: '35', humedadMin: '40', humedadMax: '85' }
  const [nuevoTipoForm, setNuevoTipoForm] = useState(emptyNuevoTipo)

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
      toast.success(editId ? t('planta.actualizada') : t('planta.registrada'))
      setShowForm(false)
      setForm(emptyForm)
      setEditId(null)
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.message ?? t('planta.errorGuardar'))
    },
  })

  const createTipo = useMutation({
    mutationFn: () =>
      tipoPlantaService.create({
        nombre:         nuevoTipoForm.nombre.trim(),
        cicloDias:      Number(nuevoTipoForm.cicloDias),
        descripcion:    nuevoTipoForm.descripcion.trim() || undefined,
        temperaturaMin: Number(nuevoTipoForm.temperaturaMin) || 15,
        temperaturaMax: Number(nuevoTipoForm.temperaturaMax) || 35,
        humedadMin:     Number(nuevoTipoForm.humedadMin) || 40,
        humedadMax:     Number(nuevoTipoForm.humedadMax) || 85,
      }),
    onSuccess: (res) => {
      const newTipo: TipoPlanta = res.data
      qc.invalidateQueries({ queryKey: ['tiposPlanta'] })
      // Auto-seleccionar el tipo recién creado
      setForm(prev => ({ ...prev, tipoPlantaId: String(newTipo.id ?? '') }))
      setNuevoTipoForm(emptyNuevoTipo)
      setShowNuevoTipo(false)
      toast.success(t('planta.tipoCreado', { nombre: newTipo.nombre }))
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.message ?? t('planta.errorCrearTipo'))
    },
  })

  const remove = useMutation({
    mutationFn: (id: number) => plantaService.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['plantas'] })
      toast.success(t('planta.eliminada'))
    },
    onError: () => toast.error(t('planta.errorEliminar')),
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
        {canWrite && (
          <button
            onClick={() => { setShowForm(true); setForm(emptyForm); setEditId(null); setShowNuevoTipo(false); setNuevoTipoForm(emptyNuevoTipo) }}
            className="flex items-center gap-2 bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800 text-sm"
          >
            <Plus size={16} /> {t('planta.nueva')}
          </button>
        )}
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
                placeholder={t('planta.codigoPlaceholder')}
              />
            </div>
            <div className="md:col-span-2 lg:col-span-3">
              <label className="text-sm text-gray-600">{t('planta.tipo')}</label>
              <div className="flex gap-2 mt-1">
                <select
                  id="tipo-planta-select"
                  className="flex-1 border rounded-lg px-3 py-2 text-sm"
                  value={form.tipoPlantaId}
                  onChange={e => {
                    setForm({ ...form, tipoPlantaId: e.target.value })
                    if (e.target.value !== '__nuevo__') setShowNuevoTipo(false)
                  }}
                >
                  <option value="">{t('common.seleccionar')}</option>
                  {tipos.map(tp => (
                    <option key={tp.id} value={tp.id}>
                      {tp.nombre} ({tp.cicloDias} {t('common.dias')})
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  title={t('planta.crearTipo')}
                  onClick={() => {
                    setShowNuevoTipo(prev => !prev)
                    if (!showNuevoTipo) setForm(prev => ({ ...prev, tipoPlantaId: '' }))
                  }}
                  className="flex items-center gap-1 bg-green-50 border border-green-300 text-green-700 hover:bg-green-100 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap"
                >
                  <PlusCircle size={14} /> {t('planta.nuevoTipo')}
                </button>
              </div>

              {/* Sub-formulario inline para crear un nuevo tipo de planta */}
              {showNuevoTipo && (
                <div className="mt-3 border border-green-200 bg-green-50 rounded-lg p-4 space-y-3">
                  <p className="text-xs font-semibold text-green-800 uppercase tracking-wide">
                    {t('planta.crearTipo')}
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <div className="col-span-2 sm:col-span-1">
                      <label className="text-xs text-gray-600">{t('planta.tipoNombre')} *</label>
                      <input
                        id="nuevo-tipo-nombre"
                        className="w-full border rounded-md px-2 py-1.5 mt-0.5 text-sm"
                        placeholder={t('planta.tipoNombrePlaceholder')}
                        value={nuevoTipoForm.nombre}
                        onChange={e => setNuevoTipoForm(prev => ({ ...prev, nombre: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">{t('planta.tipoCiclo')} *</label>
                      <input
                        id="nuevo-tipo-ciclo"
                        type="number"
                        min="1"
                        className="w-full border rounded-md px-2 py-1.5 mt-0.5 text-sm"
                        placeholder={t('planta.tipoCicloPlaceholder')}
                        value={nuevoTipoForm.cicloDias}
                        onChange={e => setNuevoTipoForm(prev => ({ ...prev, cicloDias: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">{t('planta.tipoDescripcion')}</label>
                      <input
                        className="w-full border rounded-md px-2 py-1.5 mt-0.5 text-sm"
                        placeholder={t('planta.tipoDescPlaceholder')}
                        value={nuevoTipoForm.descripcion}
                        onChange={e => setNuevoTipoForm(prev => ({ ...prev, descripcion: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">{t('planta.tipoTempMin')}</label>
                      <input
                        id="nuevo-tipo-temp-min"
                        type="number"
                        className="w-full border rounded-md px-2 py-1.5 mt-0.5 text-sm"
                        value={nuevoTipoForm.temperaturaMin}
                        onChange={e => setNuevoTipoForm(prev => ({ ...prev, temperaturaMin: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">{t('planta.tipoTempMax')}</label>
                      <input
                        id="nuevo-tipo-temp-max"
                        type="number"
                        className="w-full border rounded-md px-2 py-1.5 mt-0.5 text-sm"
                        value={nuevoTipoForm.temperaturaMax}
                        onChange={e => setNuevoTipoForm(prev => ({ ...prev, temperaturaMax: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">{t('planta.tipoHumedadMin')}</label>
                      <input
                        id="nuevo-tipo-humedad-min"
                        type="number"
                        className="w-full border rounded-md px-2 py-1.5 mt-0.5 text-sm"
                        value={nuevoTipoForm.humedadMin}
                        onChange={e => setNuevoTipoForm(prev => ({ ...prev, humedadMin: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">{t('planta.tipoHumedadMax')}</label>
                      <input
                        id="nuevo-tipo-humedad-max"
                        type="number"
                        className="w-full border rounded-md px-2 py-1.5 mt-0.5 text-sm"
                        value={nuevoTipoForm.humedadMax}
                        onChange={e => setNuevoTipoForm(prev => ({ ...prev, humedadMax: e.target.value }))}
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      id="btn-crear-tipo"
                      type="button"
                      disabled={
                        !nuevoTipoForm.nombre.trim() ||
                        !nuevoTipoForm.cicloDias ||
                        !nuevoTipoForm.temperaturaMin ||
                        !nuevoTipoForm.temperaturaMax ||
                        !nuevoTipoForm.humedadMin ||
                        !nuevoTipoForm.humedadMax ||
                        createTipo.isPending
                      }
                      onClick={() => createTipo.mutate()}
                      className="bg-green-700 text-white px-3 py-1.5 rounded-md text-xs font-medium hover:bg-green-800 disabled:opacity-50"
                    >
                      {createTipo.isPending ? t('planta.creando') : t('planta.crearYSeleccionar')}
                    </button>
                    <button
                      type="button"
                      onClick={() => { setShowNuevoTipo(false); setNuevoTipoForm(emptyNuevoTipo) }}
                      className="bg-white border border-gray-300 text-gray-600 px-3 py-1.5 rounded-md text-xs hover:bg-gray-50"
                    >
                      {t('common.cancel')}
                    </button>
                  </div>
                </div>
              )}
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('planta.zona')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={form.zonaId}
                onChange={e => setForm({ ...form, zonaId: e.target.value })}
              >
                <option value="">{t('common.seleccionar')}</option>
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
                placeholder={t('planta.observacionesPlaceholder')}
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
              onClick={() => { setShowForm(false); setForm(emptyForm); setEditId(null); setShowNuevoTipo(false); setNuevoTipoForm(emptyNuevoTipo) }}
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
                            🌾 {diasRestantes === 0 ? t('common.hoy') : `${diasRestantes} ${t('planta.diasRestantes')}`}
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
                    {canWrite && (
                      <button
                        onClick={() => startEdit(p)}
                        className="text-blue-600 hover:text-blue-800"
                        title={t('common.edit')}
                      >
                        <Pencil size={15} />
                      </button>
                    )}
                    {isAdmin && (
                      <button
                        onClick={() => {
                          if (confirm(t('planta.confirmarEliminar', { codigo: p.codigo }))) remove.mutate(p.id!)
                        }}
                        className="text-red-500 hover:text-red-700"
                        title={t('common.delete')}
                      >
                        <Trash2 size={15} />
                      </button>
                    )}
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
