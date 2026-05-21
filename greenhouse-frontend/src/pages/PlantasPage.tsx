/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { plantaService } from '../services/api'
import type { Planta } from '../types'

const estadoColor: Record<string, string> = {
  SEMBRADA: 'bg-blue-100 text-blue-800',
  EN_CRECIMIENTO: 'bg-green-100 text-green-800',
  LISTA_PARA_COSECHAR: 'bg-yellow-100 text-yellow-800',
  COSECHADA: 'bg-gray-100 text-gray-600',
  MUERTA: 'bg-red-100 text-red-800',
}

export default function PlantasPage() {
  const { t } = useTranslation()

  const { data: plantas = [], isLoading } = useQuery<Planta[]>({
    queryKey: ['plantas'],
    queryFn: () => plantaService.getAll().then(r => r.data),
  })

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{t('planta.title')}</h1>
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              <th className="px-4 py-3 text-left">{t('planta.codigo')}</th>
              <th className="px-4 py-3 text-left">{t('planta.siembra')}</th>
              <th className="px-4 py-3 text-left">{t('planta.estado')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {plantas.length === 0 && (
              <tr><td colSpan={3} className="text-center py-8 text-gray-400">{t('common.noData')}</td></tr>
            )}
            {plantas.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono font-medium">{p.codigo}</td>
                <td className="px-4 py-3 text-gray-500">{p.fechaSiembra}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${estadoColor[p.estado]}`}>
                    {t(`planta.${p.estado}`)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
