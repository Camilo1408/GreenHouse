/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { empleadoService } from '../services/api'
import type { Empleado } from '../types'

export default function EmpleadosPage() {
  const { t } = useTranslation()

  const { data: empleados = [], isLoading } = useQuery<Empleado[]>({
    queryKey: ['empleados'],
    queryFn: () => empleadoService.getAll().then(r => r.data),
  })

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">{t('nav.empleados')}</h1>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              <th className="px-4 py-3 text-left">{t('common.name')}</th>
              <th className="px-4 py-3 text-left">Email</th>
              <th className="px-4 py-3 text-left">Rol</th>
              <th className="px-4 py-3 text-left">{t('common.status')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {empleados.length === 0 && (
              <tr><td colSpan={4} className="text-center py-8 text-gray-400">{t('common.noData')}</td></tr>
            )}
            {empleados.map((e) => (
              <tr key={e.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{e.nombreCompleto}</td>
                <td className="px-4 py-3 text-gray-500">{e.email}</td>
                <td className="px-4 py-3">
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                    {e.rol}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${e.estado === 'ACTIVO' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                    {e.estado}
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
