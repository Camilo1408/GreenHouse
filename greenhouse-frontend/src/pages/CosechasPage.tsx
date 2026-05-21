/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { cosechaService } from '../services/api'
import type { Cosecha } from '../types'

export default function CosechasPage() {
  const { t } = useTranslation()

  const { data: cosechas = [], isLoading } = useQuery<Cosecha[]>({
    queryKey: ['cosechas'],
    queryFn: () => cosechaService.getAll().then(r => r.data),
  })

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">{t('cosecha.title')}</h1>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              <th className="px-4 py-3 text-left">{t('cosecha.fecha')}</th>
              <th className="px-4 py-3 text-left">{t('cosecha.peso')}</th>
              <th className="px-4 py-3 text-left">{t('cosecha.calidad')}</th>
              <th className="px-4 py-3 text-left">{t('cosecha.destino')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {cosechas.length === 0 && (
              <tr><td colSpan={4} className="text-center py-8 text-gray-400">{t('common.noData')}</td></tr>
            )}
            {cosechas.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">{c.fechaCosecha}</td>
                <td className="px-4 py-3 font-medium">{c.pesoKg} kg</td>
                <td className="px-4 py-3">
                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                    {c.calidad}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">{t(`cosecha.${c.destino}`)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
