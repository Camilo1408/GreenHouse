/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertaService, empleadoService } from '../services/api'
import toast from 'react-hot-toast'
import type { Alerta, Empleado } from '../types'
import { Bell, ChevronDown, ChevronUp, CheckCircle, XCircle, MessageSquare, Filter } from 'lucide-react'

type EstadoFilter = 'TODAS' | 'PENDIENTE' | 'ATENDIDA' | 'DESCARTADA'

const severityBg: Record<string, string> = {
  CRITICA: 'bg-red-100 text-red-800 border-red-200',
  ALTA:    'bg-orange-100 text-orange-800 border-orange-200',
  MEDIA:   'bg-yellow-100 text-yellow-800 border-yellow-200',
  BAJA:    'bg-blue-100 text-blue-800 border-blue-200',
}

const severityDot: Record<string, string> = {
  CRITICA: 'bg-red-500',
  ALTA:    'bg-orange-500',
  MEDIA:   'bg-yellow-500',
  BAJA:    'bg-blue-500',
}

const estadoBadge: Record<string, string> = {
  PENDIENTE:   'bg-amber-100 text-amber-800',
  ATENDIDA:    'bg-green-100 text-green-800',
  DESCARTADA:  'bg-gray-100 text-gray-600',
}

interface GestionForm {
  notas: string
  empleadoId: string
}

export default function AlertasPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()

  const [filtroEstado, setFiltroEstado] = useState<EstadoFilter>('TODAS')
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [gestionId, setGestionId] = useState<number | null>(null)
  const [gestionAccion, setGestionAccion] = useState<'atender' | 'descartar' | 'notas' | null>(null)
  const [gestionForm, setGestionForm] = useState<GestionForm>({ notas: '', empleadoId: '' })

  const { data: alertas = [], isLoading } = useQuery<Alerta[]>({
    queryKey: ['alertas'],
    queryFn: () => alertaService.getAll().then(r => r.data),
  })

  const { data: empleados = [] } = useQuery<Empleado[]>({
    queryKey: ['empleados'],
    queryFn: () => empleadoService.getAll().then(r => r.data),
  })

  const ejecutarGestion = useMutation({
    mutationFn: () => {
      const body = {
        notas: gestionForm.notas || undefined,
        empleadoId: gestionForm.empleadoId ? Number(gestionForm.empleadoId) : undefined,
      }
      if (gestionAccion === 'atender') return alertaService.atender(gestionId!, body)
      if (gestionAccion === 'descartar') return alertaService.descartar(gestionId!, body)
      return alertaService.agregarNotas(gestionId!, { notas: gestionForm.notas, empleadoId: body.empleadoId })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['alertas'] })
      qc.invalidateQueries({ queryKey: ['alertas-count'] })
      const msg = gestionAccion === 'atender' ? 'Alerta marcada como atendida'
        : gestionAccion === 'descartar' ? 'Alerta descartada'
        : 'Nota agregada correctamente'
      toast.success(msg)
      setGestionId(null); setGestionAccion(null)
      setGestionForm({ notas: '', empleadoId: '' })
    },
    onError: () => toast.error('Error al procesar la alerta'),
  })

  const alertasFiltradas = filtroEstado === 'TODAS'
    ? alertas
    : alertas.filter(a => a.estado === filtroEstado)

  const pendientes = alertas.filter(a => a.estado === 'PENDIENTE').length
  const criticas = alertas.filter(a => a.severidad === 'CRITICA' && a.estado === 'PENDIENTE').length

  const openGestion = (id: number, accion: 'atender' | 'descartar' | 'notas', alerta?: Alerta) => {
    setGestionId(id)
    setGestionAccion(accion)
    setGestionForm({
      notas: alerta?.notasResolucion ?? '',
      empleadoId: alerta?.atendidoPor ? String(alerta.atendidoPor.id) : '',
    })
  }

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Bell className="text-red-500" size={24} />
          {t('alerta.title')}
        </h1>
        <div className="flex gap-2">
          {pendientes > 0 && (
            <span className="bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
              {pendientes} pendiente{pendientes !== 1 ? 's' : ''}
            </span>
          )}
          {criticas > 0 && (
            <span className="bg-red-900 text-white px-3 py-1 rounded-full text-sm font-bold animate-pulse">
              {criticas} crítica{criticas !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        {(['PENDIENTE', 'ATENDIDA', 'DESCARTADA'] as const).map(estado => (
          <button
            key={estado}
            onClick={() => setFiltroEstado(filtroEstado === estado ? 'TODAS' : estado)}
            className={`p-3 rounded-xl border text-left transition-all ${
              filtroEstado === estado ? 'ring-2 ring-offset-1 ring-green-500' : ''
            } ${estadoBadge[estado]} border-transparent hover:opacity-90`}
          >
            <p className="text-2xl font-bold">{alertas.filter(a => a.estado === estado).length}</p>
            <p className="text-xs uppercase font-medium">{estado.replace('_', ' ')}</p>
          </button>
        ))}
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-3 bg-white rounded-xl p-3 shadow-sm">
        <Filter size={16} className="text-gray-400" />
        <span className="text-sm text-gray-500">{t('common.filter')}:</span>
        {(['TODAS', 'PENDIENTE', 'ATENDIDA', 'DESCARTADA'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFiltroEstado(f)}
            className={`text-xs px-3 py-1 rounded-full transition-colors ${
              filtroEstado === f
                ? 'bg-green-700 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f === 'TODAS' ? t('common.all') : t(`alerta.${f}`)}
            {' '}({f === 'TODAS' ? alertas.length : alertas.filter(a => a.estado === f).length})
          </button>
        ))}
      </div>

      {/* Alerts list */}
      <div className="space-y-2">
        {alertasFiltradas.length === 0 && (
          <div className="bg-white rounded-xl shadow-sm p-8 text-center text-gray-400">
            {t('common.noData')}
          </div>
        )}
        {alertasFiltradas.map(a => {
          const isExpanded = expandedId === a.id
          const isGestionando = gestionId === a.id

          return (
            <div
              key={a.id}
              className={`bg-white rounded-xl shadow-sm overflow-hidden border-l-4 ${
                a.estado === 'PENDIENTE'
                  ? a.severidad === 'CRITICA' ? 'border-red-600'
                  : a.severidad === 'ALTA' ? 'border-orange-500'
                  : a.severidad === 'MEDIA' ? 'border-yellow-400'
                  : 'border-blue-400'
                  : 'border-gray-200'
              }`}
            >
              {/* Main row */}
              <div
                className="px-4 py-3 flex items-center gap-3 cursor-pointer hover:bg-gray-50"
                onClick={() => setExpandedId(isExpanded ? null : a.id!)}
              >
                <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${severityDot[a.severidad]}`} />

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-sm text-gray-800 truncate">
                      {a.tipo.replace('UMBRAL_', '')} — {a.zona?.nombre}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded border font-medium flex-shrink-0 ${severityBg[a.severidad]}`}>
                      {t(`alerta.${a.severidad}`)}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded font-medium flex-shrink-0 ${estadoBadge[a.estado]}`}>
                      {t(`alerta.${a.estado}`)}
                    </span>
                  </div>
                  {a.descripcion && (
                    <p className="text-xs text-gray-500 truncate mt-0.5">{a.descripcion}</p>
                  )}
                  <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
                    <span>📅 {new Date(a.fechaGeneracion).toLocaleString()}</span>
                    {a.sensor && <span>📡 {a.sensor.codigo}</span>}
                    {a.atendidoPor && (
                      <span className="text-green-600">👤 {a.atendidoPor.nombreCompleto}</span>
                    )}
                  </div>
                </div>

                {/* Action buttons */}
                <div className="flex items-center gap-1.5 flex-shrink-0" onClick={e => e.stopPropagation()}>
                  {a.estado === 'PENDIENTE' && (
                    <>
                      <button
                        onClick={() => openGestion(a.id!, 'atender', a)}
                        className="flex items-center gap-1 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-lg hover:bg-green-200 font-medium"
                      >
                        <CheckCircle size={12} /> {t('alerta.atender')}
                      </button>
                      <button
                        onClick={() => openGestion(a.id!, 'descartar', a)}
                        className="flex items-center gap-1 text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-lg hover:bg-gray-200 font-medium"
                      >
                        <XCircle size={12} /> {t('alerta.descartar')}
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => openGestion(a.id!, 'notas', a)}
                    className="flex items-center gap-1 text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-lg hover:bg-blue-100 font-medium"
                  >
                    <MessageSquare size={12} /> {t('alerta.notas')}
                  </button>
                  {isExpanded ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
                </div>
              </div>

              {/* Expanded detail */}
              {isExpanded && (
                <div className="px-4 pb-3 bg-gray-50 border-t border-gray-100 text-sm space-y-2">
                  {a.descripcion && (
                    <div>
                      <p className="text-xs text-gray-500 font-medium mt-2">{t('alerta.descripcion')}</p>
                      <p className="text-gray-700">{a.descripcion}</p>
                    </div>
                  )}
                  {a.notasResolucion && (
                    <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-100">
                      <p className="text-xs text-yellow-700 font-medium flex items-center gap-1 mb-1">
                        <MessageSquare size={12} /> {t('alerta.notas')} de resolución
                      </p>
                      <p className="text-gray-700 text-sm">{a.notasResolucion}</p>
                    </div>
                  )}
                  {a.atendidoPor && (
                    <p className="text-xs text-gray-500">
                      👤 {t('alerta.responsable')}: <span className="font-medium text-gray-700">{a.atendidoPor.nombreCompleto}</span>
                    </p>
                  )}
                  {a.sensor && (
                    <p className="text-xs text-gray-500">
                      📡 {t('alerta.sensor')}: <span className="font-mono text-gray-700">{a.sensor.codigo}</span>
                      {' — '}{a.sensor.tipoSensor}
                    </p>
                  )}
                </div>
              )}

              {/* Gestión form */}
              {isGestionando && (
                <div className="px-4 pb-4 border-t border-gray-100 bg-white">
                  <p className="text-xs font-semibold text-gray-600 mt-3 mb-2">
                    {gestionAccion === 'atender' ? t('alerta.marcarAtendida')
                      : gestionAccion === 'descartar' ? t('alerta.descartarAlerta')
                      : t('alerta.agregarNota')}
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs text-gray-500">{t('alerta.empleadoResponsable')}</label>
                      <select
                        className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                        value={gestionForm.empleadoId}
                        onChange={e => setGestionForm({ ...gestionForm, empleadoId: e.target.value })}
                      >
                        <option value="">{t('alerta.sinAsignar')}</option>
                        {empleados.filter(e => e.estado === 'ACTIVO').map(e => (
                          <option key={e.id} value={e.id}>{e.nombreCompleto}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">
                        {gestionAccion !== 'notas' ? t('alerta.notasOpcional') : t('alerta.notas')}
                      </label>
                      <textarea
                        className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                        rows={2}
                        value={gestionForm.notas}
                        onChange={e => setGestionForm({ ...gestionForm, notas: e.target.value })}
                        placeholder={
                          gestionAccion === 'atender' ? t('alerta.comoSeResolvio')
                          : gestionAccion === 'descartar' ? t('alerta.porQueDescarta')
                          : t('alerta.agregarObservacion')
                        }
                      />
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() => ejecutarGestion.mutate()}
                      className={`px-4 py-1.5 rounded-lg text-sm font-medium text-white ${
                        gestionAccion === 'atender' ? 'bg-green-600 hover:bg-green-700'
                        : gestionAccion === 'descartar' ? 'bg-gray-600 hover:bg-gray-700'
                        : 'bg-blue-600 hover:bg-blue-700'
                      }`}
                    >
                      {gestionAccion === 'atender' ? t('alerta.confirmarAtencion')
                        : gestionAccion === 'descartar' ? t('alerta.confirmarDescarte')
                        : t('alerta.guardarNota')}
                    </button>
                    <button
                      onClick={() => { setGestionId(null); setGestionAccion(null) }}
                      className="px-4 py-1.5 rounded-lg text-sm bg-gray-100 text-gray-600 hover:bg-gray-200"
                    >
                      {t('common.cancel')}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
