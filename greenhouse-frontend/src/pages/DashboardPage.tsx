/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { alertaService, plantaService, zonaService, cosechaService } from '../services/api'
import { Leaf, Bell, Wheat, Map, AlertTriangle, ChevronRight } from 'lucide-react'
import type { Alerta } from '../types'

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: number | string
  color: string
  onClick?: () => void
}

function StatCard({ icon, label, value, color, onClick }: StatCardProps) {
  return (
    <div
      className={`bg-white rounded-xl shadow-sm p-6 flex items-center gap-4 border-l-4 ${color} ${
        onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''
      }`}
      onClick={onClick}
    >
      <div className="text-3xl">{icon}</div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
      </div>
    </div>
  )
}

const severityDot: Record<string, string> = {
  CRITICA: 'bg-red-500',
  ALTA:    'bg-orange-500',
  MEDIA:   'bg-yellow-500',
  BAJA:    'bg-blue-400',
}

const severityBg: Record<string, string> = {
  CRITICA: 'bg-red-50 border-red-200',
  ALTA:    'bg-orange-50 border-orange-200',
  MEDIA:   'bg-yellow-50 border-yellow-100',
  BAJA:    'bg-blue-50 border-blue-100',
}

export default function DashboardPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const now = new Date()

  const { data: alertaCount } = useQuery({
    queryKey: ['alertas-count'],
    queryFn: () => alertaService.countPendientes().then(r => r.data.total),
  })

  const { data: alertasPendientes = [] } = useQuery<Alerta[]>({
    queryKey: ['alertas-pendientes-dashboard'],
    queryFn: () => alertaService.getPendientes().then(r => r.data),
  })

  const { data: plantas } = useQuery({
    queryKey: ['plantas-all'],
    queryFn: () => plantaService.getAll().then(r => r.data),
  })

  const { data: zonas } = useQuery({
    queryKey: ['zonas-all'],
    queryFn: () => zonaService.getAll().then(r => r.data),
  })

  const { data: kgMes } = useQuery({
    queryKey: ['cosechas-mes'],
    queryFn: () =>
      cosechaService.totalKgMes(now.getFullYear(), now.getMonth() + 1).then(r => r.data.totalKg),
  })

  const plantasActivas = plantas?.filter(
    (p: { estado: string }) => p.estado !== 'COSECHADA' && p.estado !== 'MUERTA'
  ).length ?? 0

  const zonasActivas = zonas?.filter(
    (z: { estado: string }) => z.estado === 'ACTIVA'
  ).length ?? 0

  // Sort: CRITICA first, then ALTA, MEDIA, BAJA
  const severityOrder = { CRITICA: 0, ALTA: 1, MEDIA: 2, BAJA: 3 }
  const alertasOrdenadas = [...alertasPendientes].sort(
    (a, b) => (severityOrder[a.severidad] ?? 4) - (severityOrder[b.severidad] ?? 4)
  )

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">{t('dashboard.title')}</h1>

      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          icon={<Leaf className="text-green-600" />}
          label={t('dashboard.plantasActivas')}
          value={plantasActivas}
          color="border-green-500"
          onClick={() => navigate('/plantas')}
        />
        <StatCard
          icon={<Bell className="text-red-500" />}
          label={t('dashboard.alertasPendientes')}
          value={alertaCount ?? 0}
          color="border-red-500"
          onClick={() => navigate('/alertas')}
        />
        <StatCard
          icon={<Wheat className="text-yellow-500" />}
          label={t('dashboard.cosechasMes')}
          value={`${(kgMes ?? 0).toFixed(1)} kg`}
          color="border-yellow-500"
          onClick={() => navigate('/cosechas')}
        />
        <StatCard
          icon={<Map className="text-blue-500" />}
          label={t('dashboard.zonasActivas')}
          value={zonasActivas}
          color="border-blue-500"
          onClick={() => navigate('/zonas')}
        />
      </div>

      {/* Pending alerts section */}
      {alertasOrdenadas.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b flex items-center justify-between">
            <h2 className="text-base font-semibold text-gray-700 flex items-center gap-2">
              <AlertTriangle size={18} className="text-red-500" />
              {t('dashboard.alertasPendientesTitle')} ({alertasOrdenadas.length})
            </h2>
            <button
              onClick={() => navigate('/alertas')}
              className="text-xs text-green-700 hover:text-green-900 font-medium flex items-center gap-1"
            >
              {t('dashboard.verTodas')} <ChevronRight size={14} />
            </button>
          </div>
          <div className="divide-y divide-gray-100">
            {alertasOrdenadas.slice(0, 5).map(a => (
              <div
                key={a.id}
                className={`px-5 py-3 flex items-center gap-3 cursor-pointer hover:bg-gray-50 border-l-2 ${
                  a.severidad === 'CRITICA' ? 'border-red-500' :
                  a.severidad === 'ALTA' ? 'border-orange-400' :
                  a.severidad === 'MEDIA' ? 'border-yellow-400' : 'border-blue-300'
                }`}
                onClick={() => navigate('/alertas')}
              >
                <span className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${severityDot[a.severidad]}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-800 truncate">
                      {a.tipo.replace('UMBRAL_', '')}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium hidden sm:inline-flex items-center gap-1 border ${severityBg[a.severidad]} border-current`}>
                      {t(`alerta.${a.severidad}`)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 truncate">
                    {a.zona?.nombre} · {a.descripcion}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className="text-xs text-gray-400">
                    {new Date(a.fechaGeneracion).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <ChevronRight size={14} className="text-gray-400" />
                </div>
              </div>
            ))}
            {alertasOrdenadas.length > 5 && (
              <div
                className="px-5 py-2.5 text-center text-xs text-green-700 hover:bg-gray-50 cursor-pointer font-medium"
                onClick={() => navigate('/alertas')}
              >
                {t('dashboard.verMasAlertas', { n: alertasOrdenadas.length - 5 })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Plant status summary */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-base font-semibold text-gray-700 mb-4">{t('dashboard.estadoPlantas')}</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {['SEMBRADA', 'EN_CRECIMIENTO', 'LISTA_PARA_COSECHAR', 'COSECHADA', 'MUERTA'].map(estado => {
            const count = plantas?.filter((p: { estado: string }) => p.estado === estado).length ?? 0
            const colors: Record<string, string> = {
              SEMBRADA: 'bg-blue-50 text-blue-700',
              EN_CRECIMIENTO: 'bg-green-50 text-green-700',
              LISTA_PARA_COSECHAR: 'bg-yellow-50 text-yellow-700',
              COSECHADA: 'bg-gray-50 text-gray-500',
              MUERTA: 'bg-red-50 text-red-600',
            }
            return (
              <div key={estado} className={`text-center p-3 rounded-xl ${colors[estado]}`}>
                <p className="text-2xl font-bold">{count}</p>
                <p className="text-xs mt-1">{t(`planta.${estado}`)}</p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
