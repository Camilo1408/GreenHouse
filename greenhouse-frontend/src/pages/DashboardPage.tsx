/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { alertaService, plantaService, zonaService, cosechaService } from '../services/api'
import { Leaf, Bell, Wheat, Map } from 'lucide-react'

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: number | string
  color: string
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <div className={`bg-white rounded-xl shadow-sm p-6 flex items-center gap-4 border-l-4 ${color}`}>
      <div className="text-3xl">{icon}</div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { t } = useTranslation()
  const now = new Date()

  const { data: alertas } = useQuery({
    queryKey: ['alertas-count'],
    queryFn: () => alertaService.countPendientes().then(r => r.data.total),
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

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">{t('dashboard.title')}</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={<Leaf className="text-green-600" />}
          label={t('dashboard.plantasActivas')}
          value={plantasActivas}
          color="border-green-500"
        />
        <StatCard
          icon={<Bell className="text-red-500" />}
          label={t('dashboard.alertasPendientes')}
          value={alertas ?? 0}
          color="border-red-500"
        />
        <StatCard
          icon={<Wheat className="text-yellow-500" />}
          label={t('dashboard.cosechasMes')}
          value={`${(kgMes ?? 0).toFixed(1)} kg`}
          color="border-yellow-500"
        />
        <StatCard
          icon={<Map className="text-blue-500" />}
          label={t('dashboard.zonasActivas')}
          value={zonasActivas}
          color="border-blue-500"
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Estado de plantas por tipo</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {['SEMBRADA','EN_CRECIMIENTO','LISTA_PARA_COSECHAR','COSECHADA','MUERTA'].map(estado => {
            const count = plantas?.filter((p: { estado: string }) => p.estado === estado).length ?? 0
            return (
              <div key={estado} className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-xl font-bold text-gray-700">{count}</p>
                <p className="text-xs text-gray-500 mt-1">{t(`planta.${estado}`)}</p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
