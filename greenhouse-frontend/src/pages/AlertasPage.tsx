/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertaService } from '../services/api'
import toast from 'react-hot-toast'
import type { Alerta } from '../types'

const severityClass: Record<string, string> = {
  CRITICA: 'badge-critica',
  ALTA: 'badge-alta',
  MEDIA: 'badge-media',
  BAJA: 'badge-baja',
}

export default function AlertasPage() {
  const { t } = useTranslation()
  const qc = useQueryClient()

  const { data: alertas = [], isLoading } = useQuery<Alerta[]>({
    queryKey: ['alertas'],
    queryFn: () => alertaService.getAll().then(r => r.data),
  })

  const atender = useMutation({
    mutationFn: (id: number) => alertaService.atender(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['alertas'] }); toast.success('Alerta atendida') },
  })

  const descartar = useMutation({
    mutationFn: (id: number) => alertaService.descartar(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['alertas'] }); toast.success('Alerta descartada') },
  })

  if (isLoading) return <p className="text-gray-500">{t('common.loading')}</p>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">{t('alerta.title')}</h1>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              <th className="px-4 py-3 text-left">{t('alerta.tipo')}</th>
              <th className="px-4 py-3 text-left">{t('alerta.severidad')}</th>
              <th className="px-4 py-3 text-left">{t('alerta.zona')}</th>
              <th className="px-4 py-3 text-left">{t('alerta.fecha')}</th>
              <th className="px-4 py-3 text-left">{t('alerta.estado')}</th>
              <th className="px-4 py-3 text-left">{t('common.actions')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {alertas.length === 0 && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">{t('common.noData')}</td></tr>
            )}
            {alertas.map((a) => (
              <tr key={a.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{a.tipo}</td>
                <td className="px-4 py-3">
                  <span className={severityClass[a.severidad]}>{t(`alerta.${a.severidad}`)}</span>
                </td>
                <td className="px-4 py-3">{a.zona?.nombre}</td>
                <td className="px-4 py-3 text-gray-500">
                  {new Date(a.fechaGeneracion).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-gray-500">{a.estado}</td>
                <td className="px-4 py-3 flex gap-2">
                  {a.estado === 'PENDIENTE' && (
                    <>
                      <button
                        onClick={() => atender.mutate(a.id!)}
                        className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded hover:bg-green-200"
                      >
                        {t('alerta.atender')}
                      </button>
                      <button
                        onClick={() => descartar.mutate(a.id!)}
                        className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded hover:bg-gray-200"
                      >
                        {t('alerta.descartar')}
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
