/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  zonaService, plantaService, sensorService,
  cosechaService, tratamientoService, empleadoService,
  lecturaService, alertaService,
} from '../services/api'
import toast from 'react-hot-toast'
import type { Zona, Planta, Sensor, Cosecha, Tratamiento, Empleado, LecturaSensor, Alerta } from '../types'
import {
  ArrowLeft, Leaf, Wheat, Activity, ClipboardList,
  Plus, ChevronDown, ChevronUp, Sprout, AlertTriangle,
} from 'lucide-react'

// ── Helpers ───────────────────────────────────────────────────────────────────

function addDays(dateStr: string, days: number): Date {
  const d = new Date(dateStr + 'T00:00:00')
  d.setDate(d.getDate() + days)
  return d
}

function diasHastaCosecha(fechaSiembra: string, cicloDias: number): number {
  const cosecha = addDays(fechaSiembra, cicloDias)
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  return Math.round((cosecha.getTime() - hoy.getTime()) / (1000 * 60 * 60 * 24))
}

function formatDate(d: Date): string {
  return d.toISOString().split('T')[0]
}

const estadoColor: Record<Planta['estado'], string> = {
  SEMBRADA: 'bg-blue-100 text-blue-800',
  EN_CRECIMIENTO: 'bg-green-100 text-green-800',
  LISTA_PARA_COSECHAR: 'bg-yellow-100 text-yellow-800',
  COSECHADA: 'bg-gray-100 text-gray-600',
  MUERTA: 'bg-red-100 text-red-800',
}

const tipoTratamientoIcon: Record<string, string> = {
  FERTILIZACION: '🌱',
  PESTICIDA: '🐛',
  PODA: '✂️',
  RIEGO_MANUAL: '💧',
  REVISION: '📋',
}

// ── Main component ─────────────────────────────────────────────────────────────

export default function ZonaDetallePage() {
  const { id } = useParams<{ id: string }>()
  const zonaId = Number(id)
  const { t } = useTranslation()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const [showCosechaForm, setShowCosechaForm] = useState(false)
  const [cosechaPlantaId, setCosechaPlantaId] = useState<number | null>(null)
  const [cosechaForm, setCosechaForm] = useState({
    empleadoId: '',
    fechaCosecha: new Date().toISOString().split('T')[0],
    pesoKg: '',
    calidad: 'A' as Cosecha['calidad'],
    destino: 'VENTA' as Cosecha['destino'],
    observaciones: '',
  })

  const [showTratForm, setShowTratForm] = useState(false)
  const [tratPlantaId, setTratPlantaId] = useState<number | null>(null)
  const [tratForm, setTratForm] = useState({
    empleadoId: '',
    tipo: 'REVISION' as Tratamiento['tipoTratamiento'],
    producto: '',
    dosis: '',
    resultado: '',
    fechaHora: new Date().toISOString().slice(0, 16),
  })

  const [expandedPlanta, setExpandedPlanta] = useState<number | null>(null)

  // ── Queries ──────────────────────────────────────────────────────────────────

  const { data: zona } = useQuery<Zona>({
    queryKey: ['zona', zonaId],
    queryFn: () => zonaService.getById(zonaId).then(r => r.data),
    enabled: !!zonaId,
  })

  const { data: plantas = [] } = useQuery<Planta[]>({
    queryKey: ['plantas', 'zona', zonaId],
    queryFn: () => plantaService.getByZona(zonaId).then(r => r.data),
    enabled: !!zonaId,
  })

  const { data: sensores = [] } = useQuery<Sensor[]>({
    queryKey: ['sensores', 'zona', zonaId],
    queryFn: () => sensorService.getByZona(zonaId).then(r => r.data),
    enabled: !!zonaId,
  })

  const { data: todasCosechas = [] } = useQuery<Cosecha[]>({
    queryKey: ['cosechas'],
    queryFn: () => cosechaService.getAll().then(r => r.data),
  })

  const { data: todosTrats = [] } = useQuery<Tratamiento[]>({
    queryKey: ['tratamientos'],
    queryFn: () => tratamientoService.getAll().then(r => r.data),
  })

  const { data: empleados = [] } = useQuery<Empleado[]>({
    queryKey: ['empleados'],
    queryFn: () => empleadoService.getAll().then(r => r.data),
  })

  const { data: lecturas = [] } = useQuery<LecturaSensor[]>({
    queryKey: ['lecturas', 'zona', zonaId],
    queryFn: () => lecturaService.getByZona(zonaId).then(r => r.data),
    enabled: !!zonaId,
  })

  const { data: alertasZona = [] } = useQuery<Alerta[]>({
    queryKey: ['alertas', 'zona', zonaId],
    queryFn: () => alertaService.getByZona(zonaId).then(r => r.data),
    enabled: !!zonaId,
  })

  // Filter cosechas/tratamientos for this zone's plants
  const plantaIds = new Set(plantas.map(p => p.id))
  const cosechasZona = todasCosechas.filter(c => plantaIds.has(c.planta.id))
  const tratsZona = todosTrats.filter(tr => plantaIds.has(tr.planta.id))

  // ── Stats ─────────────────────────────────────────────────────────────────────

  const plantasActivas = plantas.filter(p => p.estado !== 'COSECHADA' && p.estado !== 'MUERTA')
  const totalKgZona = cosechasZona.reduce((sum, c) => sum + (c.pesoKg ?? 0), 0)

  // Count by estado
  const byEstado = plantas.reduce<Record<string, number>>((acc, p) => {
    acc[p.estado] = (acc[p.estado] ?? 0) + 1
    return acc
  }, {})

  // Count by tipo
  const byTipo = plantas.reduce<Record<string, number>>((acc, p) => {
    const nombre = p.tipoPlanta.nombre ?? `Tipo ${p.tipoPlanta.id}`
    acc[nombre] = (acc[nombre] ?? 0) + 1
    return acc
  }, {})

  // Próximas a cosechar (next 7 days)
  const proximasACosechar = plantasActivas.filter(p => {
    const dias = diasHastaCosecha(p.fechaSiembra, p.tipoPlanta.cicloDias ?? 90)
    return dias >= 0 && dias <= 7
  })

  // ── Mutations ─────────────────────────────────────────────────────────────────

  const registrarCosecha = useMutation({
    mutationFn: () => cosechaService.registrar({
      planta: { id: cosechaPlantaId },
      empleado: { id: Number(cosechaForm.empleadoId) },
      fechaCosecha: cosechaForm.fechaCosecha,
      pesoKg: Number(cosechaForm.pesoKg),
      calidad: cosechaForm.calidad,
      destino: cosechaForm.destino,
      observaciones: cosechaForm.observaciones || undefined,
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['cosechas'] })
      qc.invalidateQueries({ queryKey: ['plantas'] })
      qc.invalidateQueries({ queryKey: ['plantas', 'zona', zonaId] })
      toast.success('Cosecha registrada ✓')
      setShowCosechaForm(false)
      setCosechaPlantaId(null)
    },
    onError: (err: any) => toast.error(err?.response?.data?.message ?? 'Error al registrar cosecha'),
  })

  const registrarTratamiento = useMutation({
    mutationFn: () => tratamientoService.create({
      planta: { id: tratPlantaId },
      empleado: { id: Number(tratForm.empleadoId) },
      tipoTratamiento: tratForm.tipo,
      productoUtilizado: tratForm.producto || undefined,
      dosis: tratForm.dosis || undefined,
      fechaHora: tratForm.fechaHora + ':00',
      resultadoObservado: tratForm.resultado || undefined,
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tratamientos'] })
      toast.success('Tratamiento registrado ✓')
      setShowTratForm(false)
      setTratPlantaId(null)
    },
    onError: (err: any) => toast.error(err?.response?.data?.message ?? 'Error al registrar tratamiento'),
  })

  const openCosechaForm = (plantaId: number) => {
    setCosechaPlantaId(plantaId)
    setShowCosechaForm(true)
    setShowTratForm(false)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const openTratForm = (plantaId: number) => {
    setTratPlantaId(plantaId)
    setShowTratForm(true)
    setShowCosechaForm(false)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (!zona) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/zonas')}
          className="text-gray-500 hover:text-gray-700 flex items-center gap-1 text-sm"
        >
          <ArrowLeft size={16} /> Zonas
        </button>
        <span className="text-gray-300">/</span>
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Sprout className="text-green-600" size={24} />
          {zona.nombre}
          <span className={`text-sm px-2 py-0.5 rounded-full font-normal ${
            zona.estado === 'ACTIVA' ? 'bg-green-100 text-green-700' :
            zona.estado === 'EN_MANTENIMIENTO' ? 'bg-yellow-100 text-yellow-700' :
            'bg-gray-100 text-gray-500'
          }`}>
            {t(`zona.${zona.estado}`)}
          </span>
        </h1>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-green-500">
          <p className="text-xs text-gray-500 uppercase">{t('zonaDashboard.totalPlantas')}</p>
          <p className="text-3xl font-bold text-gray-800">{plantas.length}</p>
          <p className="text-xs text-gray-400 mt-1">{plantasActivas.length} activas</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-orange-400">
          <p className="text-xs text-gray-500 uppercase">{t('zonaDashboard.proximasCosechas')}</p>
          <p className="text-3xl font-bold text-orange-600">{proximasACosechar.length}</p>
          <p className="text-xs text-gray-400 mt-1">en 7 días</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-yellow-500">
          <p className="text-xs text-gray-500 uppercase">{t('zonaDashboard.totalKg')}</p>
          <p className="text-3xl font-bold text-gray-800">{totalKgZona.toFixed(1)}</p>
          <p className="text-xs text-gray-400 mt-1">kg cosechados</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-blue-400">
          <p className="text-xs text-gray-500 uppercase">Sensores</p>
          <p className="text-3xl font-bold text-gray-800">{sensores.length}</p>
          <p className="text-xs text-gray-400 mt-1">{sensores.filter(s => s.estado === 'ACTIVO').length} activos</p>
        </div>
      </div>

      {/* Summary row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Por estado */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Leaf size={16} className="text-green-500" />
            {t('zonaDashboard.porEstado')}
          </h3>
          {Object.entries(byEstado).length === 0 ? (
            <p className="text-gray-400 text-sm">{t('common.noData')}</p>
          ) : (
            <div className="space-y-2">
              {Object.entries(byEstado).map(([estado, cnt]) => (
                <div key={estado} className="flex justify-between items-center">
                  <span className={`text-xs px-2 py-0.5 rounded font-medium ${estadoColor[estado as Planta['estado']]}`}>
                    {t(`planta.${estado}`)}
                  </span>
                  <span className="font-semibold text-gray-700">{cnt}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Por tipo */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Sprout size={16} className="text-blue-500" />
            {t('zonaDashboard.porTipo')}
          </h3>
          {Object.entries(byTipo).length === 0 ? (
            <p className="text-gray-400 text-sm">{t('common.noData')}</p>
          ) : (
            <div className="space-y-2">
              {Object.entries(byTipo).map(([tipo, cnt]) => (
                <div key={tipo} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{tipo}</span>
                  <span className="font-semibold text-gray-700 bg-gray-100 px-2 py-0.5 rounded">{cnt}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Formulario cosecha inline */}
      {showCosechaForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-yellow-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Wheat size={18} className="text-yellow-500" />
            Registrar Cosecha — Planta #{cosechaPlantaId}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.empleado')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={cosechaForm.empleadoId}
                onChange={e => setCosechaForm({ ...cosechaForm, empleadoId: e.target.value })}
              >
                <option value="">— Seleccionar —</option>
                {empleados.filter(e => e.estado === 'ACTIVO').map(e => (
                  <option key={e.id} value={e.id}>{e.nombreCompleto}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.fecha')}</label>
              <input type="date" className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={cosechaForm.fechaCosecha}
                onChange={e => setCosechaForm({ ...cosechaForm, fechaCosecha: e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.peso')}</label>
              <input type="number" step="0.01" min="0" className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={cosechaForm.pesoKg}
                onChange={e => setCosechaForm({ ...cosechaForm, pesoKg: e.target.value })}
                placeholder="0.00" />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.calidad')}</label>
              <select className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={cosechaForm.calidad}
                onChange={e => setCosechaForm({ ...cosechaForm, calidad: e.target.value as Cosecha['calidad'] })}>
                <option value="A">A — Premium</option>
                <option value="B">B — Estándar</option>
                <option value="C">C — Descarte</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.destino')}</label>
              <select className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={cosechaForm.destino}
                onChange={e => setCosechaForm({ ...cosechaForm, destino: e.target.value as Cosecha['destino'] })}>
                <option value="VENTA">{t('cosecha.VENTA')}</option>
                <option value="CONSUMO_INTERNO">{t('cosecha.CONSUMO_INTERNO')}</option>
                <option value="DESCARTE">{t('cosecha.DESCARTE')}</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.observaciones')}</label>
              <input className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={cosechaForm.observaciones}
                onChange={e => setCosechaForm({ ...cosechaForm, observaciones: e.target.value })}
                placeholder="Observaciones..." />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => registrarCosecha.mutate()}
              disabled={!cosechaForm.empleadoId || !cosechaForm.pesoKg}
              className="bg-yellow-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-yellow-600 disabled:opacity-50"
            >
              <Wheat size={14} className="inline mr-1" /> {t('common.save')}
            </button>
            <button onClick={() => setShowCosechaForm(false)}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-200">
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Formulario tratamiento inline */}
      {showTratForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-green-100">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <ClipboardList size={18} className="text-green-500" />
            {t('tratamiento.nuevo')} — Planta #{tratPlantaId}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-gray-600">{t('cosecha.empleado')}</label>
              <select className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={tratForm.empleadoId}
                onChange={e => setTratForm({ ...tratForm, empleadoId: e.target.value })}>
                <option value="">— Seleccionar —</option>
                {empleados.filter(e => e.estado === 'ACTIVO').map(e => (
                  <option key={e.id} value={e.id}>{e.nombreCompleto}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('tratamiento.tipo')}</label>
              <select className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={tratForm.tipo}
                onChange={e => setTratForm({ ...tratForm, tipo: e.target.value as Tratamiento['tipoTratamiento'] })}>
                <option value="REVISION">{t('tratamiento.REVISION')}</option>
                <option value="FERTILIZACION">{t('tratamiento.FERTILIZACION')}</option>
                <option value="PESTICIDA">{t('tratamiento.PESTICIDA')}</option>
                <option value="PODA">{t('tratamiento.PODA')}</option>
                <option value="RIEGO_MANUAL">{t('tratamiento.RIEGO_MANUAL')}</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('tratamiento.fecha')}</label>
              <input type="datetime-local" className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={tratForm.fechaHora}
                onChange={e => setTratForm({ ...tratForm, fechaHora: e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('tratamiento.producto')}</label>
              <input className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={tratForm.producto}
                onChange={e => setTratForm({ ...tratForm, producto: e.target.value })}
                placeholder="Nombre del producto" />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('tratamiento.dosis')}</label>
              <input className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={tratForm.dosis}
                onChange={e => setTratForm({ ...tratForm, dosis: e.target.value })}
                placeholder="Ej: 5 ml/L" />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('tratamiento.resultado')}</label>
              <input className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={tratForm.resultado}
                onChange={e => setTratForm({ ...tratForm, resultado: e.target.value })}
                placeholder="Resultado observado..." />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => registrarTratamiento.mutate()}
              disabled={!tratForm.empleadoId}
              className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 disabled:opacity-50"
            >
              {t('common.save')}
            </button>
            <button onClick={() => setShowTratForm(false)}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-200">
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Lista de plantas */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="px-4 py-3 bg-gray-50 border-b flex items-center justify-between">
          <h3 className="font-semibold text-gray-700 flex items-center gap-2">
            <Leaf size={16} className="text-green-500" />
            Plantas de esta zona ({plantas.length})
          </h3>
        </div>
        {plantas.length === 0 ? (
          <p className="text-center py-8 text-gray-400">{t('common.noData')}</p>
        ) : (
          <div className="divide-y divide-gray-100">
            {plantas.map(p => {
              const cicloDias = p.tipoPlanta.cicloDias ?? 90
              const dias = diasHastaCosecha(p.fechaSiembra, cicloDias)
              const fechaCosechaEst = formatDate(addDays(p.fechaSiembra, cicloDias))
              const esProxima = dias >= 0 && dias <= 7
              const vencida = dias < 0 && p.estado !== 'COSECHADA' && p.estado !== 'MUERTA'
              const cosechasDePlanta = cosechasZona.filter(c => c.planta.id === p.id)
              const tratsDePlanta = tratsZona.filter(tr => tr.planta.id === p.id)
              const isExpanded = expandedPlanta === p.id

              return (
                <div key={p.id}>
                  <div
                    className={`px-4 py-3 flex items-center justify-between hover:bg-gray-50 cursor-pointer ${
                      esProxima ? 'bg-orange-50' : ''
                    }`}
                    onClick={() => setExpandedPlanta(isExpanded ? null : p.id!)}
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <span className="font-mono font-medium text-sm">{p.codigo}</span>
                      <span className="text-gray-500 text-sm">{p.tipoPlanta.nombre ?? `Tipo ${p.tipoPlanta.id}`}</span>
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${estadoColor[p.estado]}`}>
                        {t(`planta.${p.estado}`)}
                      </span>
                      {esProxima && (
                        <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full font-medium">
                          🌾 {dias === 0 ? '¡Hoy!' : `${dias}d`}
                        </span>
                      )}
                      {vencida && (
                        <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-medium">
                          ⚠ +{Math.abs(dias)}d
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <span>📅 {fechaCosechaEst}</span>
                      {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="px-4 pb-4 bg-gray-50 border-t border-gray-100">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
                        {/* Info planta */}
                        <div className="text-sm space-y-1">
                          <p><span className="text-gray-500">Siembra:</span> <span className="font-medium">{p.fechaSiembra}</span></p>
                          <p><span className="text-gray-500">Cosecha est.:</span> <span className="font-medium">{fechaCosechaEst}</span></p>
                          <p><span className="text-gray-500">Ciclo:</span> <span className="font-medium">{cicloDias} días</span></p>
                          {p.observaciones && (
                            <p><span className="text-gray-500">Notas:</span> <span className="italic">{p.observaciones}</span></p>
                          )}
                        </div>

                        {/* Acciones */}
                        <div className="flex flex-col gap-2">
                          {p.estado !== 'COSECHADA' && p.estado !== 'MUERTA' && (
                            <button
                              onClick={e => { e.stopPropagation(); openCosechaForm(p.id!) }}
                              className="flex items-center gap-2 bg-yellow-500 text-white px-3 py-1.5 rounded-lg text-xs hover:bg-yellow-600"
                            >
                              <Wheat size={13} /> {t('zonaDashboard.cosechar')}
                            </button>
                          )}
                          <button
                            onClick={e => { e.stopPropagation(); openTratForm(p.id!) }}
                            className="flex items-center gap-2 bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs hover:bg-green-700"
                          >
                            <Plus size={13} /> {t('tratamiento.nuevo')}
                          </button>
                        </div>
                      </div>

                      {/* Cosechas de esta planta */}
                      {cosechasDePlanta.length > 0 && (
                        <div className="mt-4">
                          <p className="text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1">
                            <Wheat size={12} /> Cosechas ({cosechasDePlanta.length})
                          </p>
                          <div className="space-y-1">
                            {cosechasDePlanta.map(c => (
                              <div key={c.id} className="flex gap-3 text-xs text-gray-600 bg-white rounded px-2 py-1.5">
                                <span>{c.fechaCosecha}</span>
                                <span className="font-medium">{c.pesoKg} kg</span>
                                <span className="bg-green-100 text-green-700 px-1 rounded">{c.calidad}</span>
                                <span className="text-gray-400">{c.destino?.replace('_', ' ')}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Tratamientos de esta planta */}
                      {tratsDePlanta.length > 0 && (
                        <div className="mt-4">
                          <p className="text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1">
                            <ClipboardList size={12} /> Tratamientos ({tratsDePlanta.length})
                          </p>
                          <div className="space-y-1">
                            {tratsDePlanta.slice(0, 5).map(tr => (
                              <div key={tr.id} className="flex gap-3 text-xs text-gray-600 bg-white rounded px-2 py-1.5">
                                <span>{tipoTratamientoIcon[tr.tipoTratamiento]}</span>
                                <span className="font-medium">{t(`tratamiento.${tr.tipoTratamiento}`)}</span>
                                {tr.productoUtilizado && <span className="text-gray-400">— {tr.productoUtilizado}</span>}
                                <span className="text-gray-400 ml-auto">{tr.fechaHora?.slice(0, 10)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Alertas de la zona */}
      {alertasZona.filter(a => a.estado === 'PENDIENTE').length > 0 && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="px-4 py-3 bg-red-50 border-b border-red-100 flex items-center justify-between">
            <h3 className="font-semibold text-red-700 flex items-center gap-2">
              <AlertTriangle size={16} />
              Alertas pendientes ({alertasZona.filter(a => a.estado === 'PENDIENTE').length})
            </h3>
            <button
              onClick={() => navigate('/alertas')}
              className="text-xs text-red-600 hover:underline"
            >
              Gestionar →
            </button>
          </div>
          <div className="divide-y divide-gray-100">
            {alertasZona.filter(a => a.estado === 'PENDIENTE').map(a => (
              <div key={a.id} className="px-4 py-2.5 flex items-center gap-3 text-sm">
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  a.severidad === 'CRITICA' ? 'bg-red-500' :
                  a.severidad === 'ALTA' ? 'bg-orange-500' :
                  a.severidad === 'MEDIA' ? 'bg-yellow-400' : 'bg-blue-400'
                }`} />
                <span className="font-medium text-gray-700">{a.tipo.replace('UMBRAL_', '')}</span>
                <span className="text-gray-500 truncate flex-1">{a.descripcion}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                  a.severidad === 'CRITICA' ? 'bg-red-100 text-red-700' :
                  a.severidad === 'ALTA' ? 'bg-orange-100 text-orange-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>{a.severidad}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sensores con estadísticas de lecturas */}
      {sensores.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-4">
          <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Activity size={16} className="text-blue-500" />
            {t('zonaDashboard.sensores')} ({sensores.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {sensores.map(s => {
              const sLecturas = lecturas.filter(l => l.sensor?.id === s.id || (l.sensor as any)?.id === s.id)
              const valores = sLecturas.map(l => l.valor).filter(v => v !== null && v !== undefined)
              const ultima = sLecturas[0]
              const minVal = valores.length ? Math.min(...valores) : null
              const maxVal = valores.length ? Math.max(...valores) : null
              const avgVal = valores.length ? valores.reduce((a, b) => a + b, 0) / valores.length : null
              const unidad = sLecturas[0]?.unidad ?? ''

              // Check if last reading is out of range
              const fueraRango = ultima && s.umbralMin != null && s.umbralMax != null
                ? (ultima.valor < s.umbralMin! || ultima.valor > s.umbralMax!)
                : false

              return (
                <div
                  key={s.id}
                  className={`rounded-lg border p-3 ${
                    fueraRango ? 'border-red-200 bg-red-50' :
                    s.estado === 'ACTIVO' ? 'border-green-100 bg-green-50' :
                    'border-gray-100 bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className={`w-2 h-2 rounded-full ${
                          fueraRango ? 'bg-red-500' :
                          s.estado === 'ACTIVO' ? 'bg-green-500' : 'bg-gray-400'
                        }`} />
                        <span className="text-xs font-semibold text-gray-700">{s.tipoSensor}</span>
                      </div>
                      <span className="font-mono text-xs text-gray-400">{s.codigo}</span>
                    </div>
                    {fueraRango && (
                      <span className="text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded font-medium">
                        ⚠ Fuera de rango
                      </span>
                    )}
                  </div>

                  {ultima ? (
                    <>
                      <div className="text-2xl font-bold text-gray-800 mb-1">
                        {ultima.valor.toFixed(1)}
                        <span className="text-sm font-normal text-gray-400 ml-1">{unidad}</span>
                      </div>
                      <div className="grid grid-cols-3 gap-1 text-xs text-center">
                        <div className="bg-white rounded p-1">
                          <p className="text-gray-400">Mín</p>
                          <p className="font-semibold text-blue-600">{minVal?.toFixed(1)}</p>
                        </div>
                        <div className="bg-white rounded p-1">
                          <p className="text-gray-400">Prom</p>
                          <p className="font-semibold text-gray-700">{avgVal?.toFixed(1)}</p>
                        </div>
                        <div className="bg-white rounded p-1">
                          <p className="text-gray-400">Máx</p>
                          <p className="font-semibold text-red-500">{maxVal?.toFixed(1)}</p>
                        </div>
                      </div>
                      {s.umbralMin != null && s.umbralMax != null && (
                        <p className="text-xs text-gray-400 mt-1 text-center">
                          Umbral: {s.umbralMin}–{s.umbralMax} {unidad}
                        </p>
                      )}
                    </>
                  ) : (
                    <p className="text-xs text-gray-400 italic">Sin lecturas registradas</p>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Historial de cosechas de la zona */}
      {cosechasZona.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="px-4 py-3 bg-gray-50 border-b">
            <h3 className="font-semibold text-gray-700 flex items-center gap-2">
              <Wheat size={16} className="text-yellow-500" />
              {t('zonaDashboard.historialCosechas')} — {totalKgZona.toFixed(1)} kg total
            </h3>
          </div>
          <table className="w-full text-sm">
            <thead className="text-gray-500 text-xs uppercase">
              <tr>
                <th className="px-4 py-2 text-left">Fecha</th>
                <th className="px-4 py-2 text-left">Planta</th>
                <th className="px-4 py-2 text-left">Peso</th>
                <th className="px-4 py-2 text-left">Calidad</th>
                <th className="px-4 py-2 text-left">Destino</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {cosechasZona.map(c => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2">{c.fechaCosecha}</td>
                  <td className="px-4 py-2 font-mono text-xs">{c.planta.codigo ?? `#${c.planta.id}`}</td>
                  <td className="px-4 py-2 font-medium">{c.pesoKg} kg</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      c.calidad === 'A' ? 'bg-green-100 text-green-700' :
                      c.calidad === 'B' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-600'
                    }`}>
                      {c.calidad}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-500 text-xs">{c.destino?.replace('_', ' ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
