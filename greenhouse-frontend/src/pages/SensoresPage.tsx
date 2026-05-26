/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sensorService, zonaService, lecturaService } from '../services/api'
import toast from 'react-hot-toast'
import type { Sensor, Zona, LecturaSensor } from '../types'
import { Plus, Pencil, Trash2, Activity, Zap, Thermometer, Droplets, Wind, Sun, FlaskConical } from 'lucide-react'

type TipoSensor = Sensor['tipoSensor']

const SENSOR_CONFIG: Record<TipoSensor, {
  icon: React.ReactNode
  unit: string
  min: number
  max: number
  defaultMin: number
  defaultMax: number
  color: string
}> = {
  TEMPERATURA: {
    icon: <Thermometer size={16} />,
    unit: '°C',
    min: 0,
    max: 60,
    defaultMin: 15,
    defaultMax: 30,
    color: 'text-orange-500',
  },
  HUMEDAD: {
    icon: <Droplets size={16} />,
    unit: '%',
    min: 0,
    max: 100,
    defaultMin: 40,
    defaultMax: 80,
    color: 'text-blue-500',
  },
  CO2: {
    icon: <Wind size={16} />,
    unit: 'ppm',
    min: 0,
    max: 5000,
    defaultMin: 400,
    defaultMax: 1500,
    color: 'text-gray-600',
  },
  PH: {
    icon: <FlaskConical size={16} />,
    unit: 'pH',
    min: 0,
    max: 14,
    defaultMin: 5.5,
    defaultMax: 7.0,
    color: 'text-purple-500',
  },
  LUZ: {
    icon: <Sun size={16} />,
    unit: 'lux',
    min: 0,
    max: 100000,
    defaultMin: 1000,
    defaultMax: 50000,
    color: 'text-yellow-500',
  },
}

/** Gauge visual — valor entre 0 y 100% del rango */
function SensorGauge({ valor, umbralMin, umbralMax, config }: {
  valor: number
  umbralMin: number
  umbralMax: number
  config: typeof SENSOR_CONFIG[TipoSensor]
}) {
  const rangeTotal = config.max - config.min
  const pct = Math.min(100, Math.max(0, ((valor - config.min) / rangeTotal) * 100))
  const minPct = ((umbralMin - config.min) / rangeTotal) * 100
  const maxPct = ((umbralMax - config.min) / rangeTotal) * 100
  const enRango = valor >= umbralMin && valor <= umbralMax

  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{config.min}{config.unit}</span>
        <span>{config.max}{config.unit}</span>
      </div>
      <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
        {/* Rango óptimo */}
        <div
          className="absolute top-0 h-full bg-green-200 opacity-70"
          style={{ left: `${minPct}%`, width: `${maxPct - minPct}%` }}
        />
        {/* Valor actual */}
        <div
          className={`absolute top-0 h-full w-2 rounded-full transition-all ${enRango ? 'bg-green-600' : 'bg-red-500'}`}
          style={{ left: `calc(${pct}% - 4px)` }}
        />
      </div>
      <div className="flex justify-between text-xs mt-1">
        <span className="text-gray-400">Umbral: {umbralMin}–{umbralMax} {config.unit}</span>
        <span className={`font-medium ${enRango ? 'text-green-600' : 'text-red-500'}`}>
          {enRango ? '✓ Normal' : '⚠ Fuera de rango'}
        </span>
      </div>
    </div>
  )
}

const emptySensorForm = {
  codigo: '',
  tipoSensor: 'TEMPERATURA' as TipoSensor,
  zonaId: '',
  umbralMin: '',
  umbralMax: '',
  fechaInstalacion: new Date().toISOString().split('T')[0],
}

export default function SensoresPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()

  const [selectedZonaId, setSelectedZonaId] = useState<number | null>(null)
  const [showSensorForm, setShowSensorForm] = useState(false)
  const [sensorForm, setSensorForm] = useState(emptySensorForm)
  const [editSensorId, setEditSensorId] = useState<number | null>(null)

  // Simulator state
  const [simSensorId, setSimSensorId] = useState<number | null>(null)
  const [simValor, setSimValor] = useState('')
  const [lastReadings, setLastReadings] = useState<Record<number, number>>({})

  const { data: zonas = [] } = useQuery<Zona[]>({
    queryKey: ['zonas'],
    queryFn: () => zonaService.getAll().then(r => r.data),
  })

  const { data: sensores = [], isLoading } = useQuery<Sensor[]>({
    queryKey: ['sensores'],
    queryFn: () => sensorService.getAll().then(r => r.data),
  })

  const sensoresFiltrados = selectedZonaId
    ? sensores.filter(s => s.zona.id === selectedZonaId)
    : sensores

  const saveSensor = useMutation({
    mutationFn: () => {
      const cfg = SENSOR_CONFIG[sensorForm.tipoSensor]
      const payload = {
        codigo: sensorForm.codigo,
        tipoSensor: sensorForm.tipoSensor,
        zona: { id: Number(sensorForm.zonaId) },
        estado: 'ACTIVO',
        umbralMin: sensorForm.umbralMin ? Number(sensorForm.umbralMin) : cfg.defaultMin,
        umbralMax: sensorForm.umbralMax ? Number(sensorForm.umbralMax) : cfg.defaultMax,
        fechaInstalacion: sensorForm.fechaInstalacion || undefined,
      }
      return editSensorId
        ? sensorService.update(editSensorId, payload)
        : sensorService.create(payload)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sensores'] })
      toast.success(editSensorId ? 'Sensor actualizado' : 'Sensor creado')
      setShowSensorForm(false)
      setSensorForm(emptySensorForm)
      setEditSensorId(null)
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.message ?? 'Error al guardar sensor')
    },
  })

  const removeSensor = useMutation({
    mutationFn: (id: number) => sensorService.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sensores'] })
      toast.success('Sensor eliminado')
    },
  })

  const registrarLectura = useMutation({
    mutationFn: ({ sensorId, valor }: { sensorId: number; valor: number }) => {
      const sensor = sensores.find(s => s.id === sensorId)!
      const cfg = SENSOR_CONFIG[sensor.tipoSensor]
      return lecturaService.registrar({
        sensor: { id: sensorId },
        valor,
        unidad: cfg.unit,
        fuente: 'MANUAL',
      })
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['alertas'] })
      setLastReadings(prev => ({ ...prev, [vars.sensorId]: vars.valor }))
      toast.success('Lectura registrada ✓ (alertas verificadas)')
      setSimValor('')
      setSimSensorId(null)
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.message ?? 'Error al registrar lectura')
    },
  })

  const startEditSensor = (s: Sensor) => {
    setSensorForm({
      codigo: s.codigo,
      tipoSensor: s.tipoSensor,
      zonaId: String(s.zona.id),
      umbralMin: String(s.umbralMin ?? ''),
      umbralMax: String(s.umbralMax ?? ''),
      fechaInstalacion: s.fechaInstalacion ?? '',
    })
    setEditSensorId(s.id!)
    setShowSensorForm(true)
  }

  const handleSimular = (sensor: Sensor) => {
    const cfg = SENSOR_CONFIG[sensor.tipoSensor]
    // Auto-generate a realistic value near the middle of the optimal range
    const rango = cfg.defaultMax - cfg.defaultMin
    const auto = (cfg.defaultMin + rango * 0.5).toFixed(1)
    setSimSensorId(sensor.id!)
    setSimValor(auto)
  }

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Activity className="text-green-600" size={24} />
          {t('sensor.title')}
        </h1>
        <button
          onClick={() => { setShowSensorForm(true); setSensorForm(emptySensorForm); setEditSensorId(null) }}
          className="flex items-center gap-2 bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800 text-sm"
        >
          <Plus size={16} /> {t('sensor.nuevo')}
        </button>
      </div>

      {/* Filtro por zona */}
      <div className="mb-4 flex items-center gap-3">
        <label className="text-sm text-gray-600 font-medium">Filtrar por zona:</label>
        <select
          className="border rounded-lg px-3 py-2 text-sm"
          value={selectedZonaId ?? ''}
          onChange={e => setSelectedZonaId(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">Todas las zonas</option>
          {zonas.map(z => (
            <option key={z.id} value={z.id}>{z.nombre}</option>
          ))}
        </select>
      </div>

      {/* Formulario nuevo sensor */}
      {showSensorForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6 border border-green-100">
          <h2 className="font-semibold text-gray-700 mb-4">
            {editSensorId ? t('common.edit') : t('sensor.nuevo')}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-gray-600">{t('sensor.codigo')}</label>
              <input
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={sensorForm.codigo}
                onChange={e => setSensorForm({ ...sensorForm, codigo: e.target.value })}
                placeholder="SEN-001"
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('sensor.tipo')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={sensorForm.tipoSensor}
                onChange={e => setSensorForm({ ...sensorForm, tipoSensor: e.target.value as TipoSensor })}
              >
                {(Object.keys(SENSOR_CONFIG) as TipoSensor[]).map(k => (
                  <option key={k} value={k}>{t(`sensor.${k}`)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('sensor.zona')}</label>
              <select
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={sensorForm.zonaId}
                onChange={e => setSensorForm({ ...sensorForm, zonaId: e.target.value })}
              >
                <option value="">— Seleccionar —</option>
                {zonas.map(z => (
                  <option key={z.id} value={z.id}>{z.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">
                {t('sensor.umbralMin')} ({SENSOR_CONFIG[sensorForm.tipoSensor].unit})
              </label>
              <input
                type="number"
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={sensorForm.umbralMin}
                onChange={e => setSensorForm({ ...sensorForm, umbralMin: e.target.value })}
                placeholder={String(SENSOR_CONFIG[sensorForm.tipoSensor].defaultMin)}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">
                {t('sensor.umbralMax')} ({SENSOR_CONFIG[sensorForm.tipoSensor].unit})
              </label>
              <input
                type="number"
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={sensorForm.umbralMax}
                onChange={e => setSensorForm({ ...sensorForm, umbralMax: e.target.value })}
                placeholder={String(SENSOR_CONFIG[sensorForm.tipoSensor].defaultMax)}
              />
            </div>
            <div>
              <label className="text-sm text-gray-600">{t('sensor.instalacion')}</label>
              <input
                type="date"
                className="w-full border rounded-lg px-3 py-2 mt-1 text-sm"
                value={sensorForm.fechaInstalacion}
                onChange={e => setSensorForm({ ...sensorForm, fechaInstalacion: e.target.value })}
              />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => saveSensor.mutate()}
              disabled={!sensorForm.codigo || !sensorForm.zonaId}
              className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-800 disabled:opacity-50"
            >
              {t('common.save')}
            </button>
            <button
              onClick={() => { setShowSensorForm(false); setSensorForm(emptySensorForm); setEditSensorId(null) }}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-200"
            >
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Grid de sensores */}
      {sensoresFiltrados.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center text-gray-400">
          {t('common.noData')}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {sensoresFiltrados.map(sensor => {
            const cfg = SENSOR_CONFIG[sensor.tipoSensor]
            const umbralMin = sensor.umbralMin ?? cfg.defaultMin
            const umbralMax = sensor.umbralMax ?? cfg.defaultMax
            const lastVal = lastReadings[sensor.id!]
            const isSimulating = simSensorId === sensor.id

            return (
              <div
                key={sensor.id}
                className={`bg-white rounded-xl shadow-sm p-4 border-l-4 ${
                  sensor.estado === 'ACTIVO' ? 'border-green-500' :
                  sensor.estado === 'EN_MANTENIMIENTO' ? 'border-yellow-400' : 'border-gray-300'
                }`}
              >
                {/* Header */}
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <div className={`flex items-center gap-1.5 font-semibold ${cfg.color}`}>
                      {cfg.icon}
                      <span>{t(`sensor.${sensor.tipoSensor}`)}</span>
                    </div>
                    <p className="font-mono text-xs text-gray-500 mt-0.5">{sensor.codigo}</p>
                    <p className="text-xs text-gray-400">{sensor.zona.nombre ?? `Zona ${sensor.zona.id}`}</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      sensor.estado === 'ACTIVO' ? 'bg-green-100 text-green-700' :
                      sensor.estado === 'EN_MANTENIMIENTO' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-500'
                    }`}>
                      {t(`sensor.${sensor.estado}`)}
                    </span>
                    <button onClick={() => startEditSensor(sensor)} className="text-blue-500 hover:text-blue-700 p-1">
                      <Pencil size={13} />
                    </button>
                    <button onClick={() => { if (confirm('¿Eliminar sensor?')) removeSensor.mutate(sensor.id!) }} className="text-red-400 hover:text-red-600 p-1">
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>

                {/* Last reading */}
                {lastVal !== undefined && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-500 mb-1">{t('sensor.ultimaLectura')}</p>
                    <p className="text-3xl font-bold text-gray-800">
                      {lastVal} <span className="text-sm text-gray-400">{cfg.unit}</span>
                    </p>
                    <div className="mt-2">
                      <SensorGauge valor={lastVal} umbralMin={umbralMin} umbralMax={umbralMax} config={cfg} />
                    </div>
                  </div>
                )}

                {/* Simulator */}
                {isSimulating ? (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs font-medium text-gray-600 mb-2 flex items-center gap-1">
                      <Zap size={12} className="text-yellow-500" />
                      {t('sensor.simulador')}
                    </p>
                    <div className="flex gap-2 items-center">
                      <input
                        type="number"
                        step="0.1"
                        className="flex-1 border rounded-lg px-2 py-1.5 text-sm"
                        value={simValor}
                        onChange={e => setSimValor(e.target.value)}
                        placeholder={`Valor en ${cfg.unit}`}
                      />
                      <span className="text-xs text-gray-400">{cfg.unit}</span>
                    </div>
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={() => {
                          if (simValor) {
                            registrarLectura.mutate({ sensorId: sensor.id!, valor: Number(simValor) })
                          }
                        }}
                        disabled={!simValor}
                        className="flex-1 bg-green-600 text-white py-1.5 rounded-lg text-xs hover:bg-green-700 disabled:opacity-50"
                      >
                        {t('sensor.registrarLectura')}
                      </button>
                      <button
                        onClick={() => setSimSensorId(null)}
                        className="px-3 py-1.5 bg-gray-100 text-gray-600 rounded-lg text-xs hover:bg-gray-200"
                      >
                        ✕
                      </button>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      Rango óptimo: {umbralMin}–{umbralMax} {cfg.unit}
                    </p>
                  </div>
                ) : (
                  <button
                    onClick={() => handleSimular(sensor)}
                    className="mt-2 w-full flex items-center justify-center gap-1.5 border border-green-300 text-green-700 py-1.5 rounded-lg text-xs hover:bg-green-50 transition-colors"
                  >
                    <Zap size={12} />
                    {t('sensor.simulador')}
                  </button>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
