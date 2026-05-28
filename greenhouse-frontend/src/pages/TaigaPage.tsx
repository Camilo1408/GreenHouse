/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import { useState, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { taigaService } from '../services/api'
import { BookOpen, RefreshCw, CheckCircle2, Circle, Tag, ChevronDown, ChevronRight, Search, ExternalLink } from 'lucide-react'

// ── Tipos ─────────────────────────────────────────────────────────────────────

interface Historia {
  id: number
  ref: number
  subject: string
  status: string
  statusColor: string
  isClosed: boolean
  sprint: string | null
  points: number | null
  tags: string[]
}

type Filtro = 'all' | 'open' | 'closed'

// ── Colores de etiquetas ──────────────────────────────────────────────────────

const TAG_COLORS = [
  'bg-sky-100 text-sky-700',
  'bg-violet-100 text-violet-700',
  'bg-amber-100 text-amber-700',
  'bg-rose-100 text-rose-700',
  'bg-teal-100 text-teal-700',
  'bg-lime-100 text-lime-700',
]

function tagColor(tag: string) {
  let hash = 0
  for (let i = 0; i < tag.length; i++) hash = tag.charCodeAt(i) + ((hash << 5) - hash)
  return TAG_COLORS[Math.abs(hash) % TAG_COLORS.length]
}

// ── Componente de una historia ────────────────────────────────────────────────

function HistoriaCard({ h }: { h: Historia }) {
  return (
    <div className={`flex items-start gap-3 py-3 px-4 rounded-lg transition-colors ${
      h.isClosed ? 'bg-gray-50 opacity-70' : 'bg-white hover:bg-green-50/40'
    }`}>
      {/* Ícono estado */}
      <div className="mt-0.5 flex-shrink-0">
        {h.isClosed
          ? <CheckCircle2 size={16} className="text-green-500" />
          : <Circle      size={16} className="text-gray-300" />
        }
      </div>

      {/* Contenido */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Referencia */}
          <span className="text-xs font-mono text-gray-400 flex-shrink-0">#{h.ref}</span>

          {/* Título */}
          <span className={`text-sm font-medium leading-snug ${h.isClosed ? 'line-through text-gray-400' : 'text-gray-800'}`}>
            {h.subject}
          </span>
        </div>

        {/* Etiquetas y badge de estado */}
        <div className="flex items-center gap-2 mt-1 flex-wrap">
          {/* Badge de estado */}
          <span
            className="px-2 py-0.5 rounded text-xs font-medium text-white flex-shrink-0"
            style={{ backgroundColor: h.statusColor || '#999' }}
          >
            {h.status}
          </span>

          {/* Tags */}
          {h.tags.map(tag => (
            <span key={tag} className={`flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${tagColor(tag)}`}>
              <Tag size={10} />
              {tag}
            </span>
          ))}

          {/* Puntos */}
          {h.points != null && (
            <span className="ml-auto text-xs text-gray-400 flex-shrink-0 font-mono">
              {h.points} pts
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Componente de grupo (sprint / backlog) ────────────────────────────────────

function SprintGroup({ nombre, historias }: { nombre: string; historias: Historia[] }) {
  const [open, setOpen] = useState(true)
  const cerradas = historias.filter(h => h.isClosed).length
  const puntos   = historias.reduce((s, h) => s + (h.points ?? 0), 0)

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-4">
      {/* Cabecera del sprint */}
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
      >
        {open
          ? <ChevronDown  size={16} className="text-gray-400 flex-shrink-0" />
          : <ChevronRight size={16} className="text-gray-400 flex-shrink-0" />
        }
        <span className="font-semibold text-gray-700 flex-1">{nombre}</span>
        <span className="text-xs text-gray-500 bg-white border border-gray-200 rounded px-2 py-0.5">
          {historias.length} HU
        </span>
        <span className={`text-xs rounded px-2 py-0.5 font-medium ${
          cerradas === historias.length
            ? 'bg-green-100 text-green-700'
            : cerradas > 0
              ? 'bg-yellow-100 text-yellow-700'
              : 'bg-gray-100 text-gray-600'
        }`}>
          {cerradas}/{historias.length} ✓
        </span>
        {puntos > 0 && (
          <span className="text-xs text-gray-400 font-mono bg-white border border-gray-100 rounded px-2 py-0.5">
            {puntos} pts
          </span>
        )}
      </button>

      {/* Historias del sprint */}
      {open && (
        <div className="divide-y divide-gray-50 px-2 py-1">
          {historias.map(h => (
            <HistoriaCard key={h.id} h={h} />
          ))}
        </div>
      )}
    </div>
  )
}

// ── Página principal ──────────────────────────────────────────────────────────

export default function TaigaPage() {
  const { t } = useTranslation()
  const [filtro, setFiltro]   = useState<Filtro>('all')
  const [buscar, setBuscar]   = useState('')

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery<Historia[]>({
    queryKey: ['taiga-historias'],
    queryFn: async () => {
      const resp = await taigaService.getHistorias()
      // 503 viene como respuesta OK de axios pero con campo "error"
      if (resp.data?.error) {
        throw new Error(resp.data.mensaje ?? 'Error de Taiga')
      }
      return resp.data as Historia[]
    },
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 min
  })

  // Filtrar por texto y estado
  const historiasFiltradas = useMemo(() => {
    if (!data) return []
    return data.filter(h => {
      const matchFiltro =
        filtro === 'all'    ? true :
        filtro === 'open'   ? !h.isClosed :
        /* closed */          h.isClosed
      const matchBuscar = buscar.trim() === '' ||
        h.subject.toLowerCase().includes(buscar.toLowerCase()) ||
        String(h.ref).includes(buscar)
      return matchFiltro && matchBuscar
    })
  }, [data, filtro, buscar])

  // Agrupar por sprint
  const grupos = useMemo(() => {
    const map = new Map<string, Historia[]>()
    for (const h of historiasFiltradas) {
      const key = h.sprint ?? '__backlog__'
      if (!map.has(key)) map.set(key, [])
      map.get(key)!.push(h)
    }
    // Ordenar: sprints primero (numéricamente), backlog al final
    return Array.from(map.entries()).sort(([a], [b]) => {
      if (a === '__backlog__') return 1
      if (b === '__backlog__') return -1
      return a.localeCompare(b, undefined, { numeric: true })
    })
  }, [historiasFiltradas])

  // Estadísticas globales
  const totalAll    = data?.length ?? 0
  const cerradasAll = data?.filter(h => h.isClosed).length ?? 0
  const puntosAll   = data?.reduce((s, h) => s + (h.points ?? 0), 0) ?? 0

  // ── Error específico de credenciales ─────────────────────────────────────
  const errMsg = (error as Error)?.message ?? ''
  const sinCredenciales = errMsg.includes('no_credentials') || errMsg.includes('no configuradas')

  return (
    <div>
      {/* Cabecera */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <BookOpen className="text-indigo-600" size={24} />
            {t('taiga.title')}
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">{t('taiga.subtitle')}</p>
        </div>

        {/* Botón sincronizar */}
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm disabled:opacity-60 transition-colors"
        >
          <RefreshCw size={15} className={isFetching ? 'animate-spin' : ''} />
          {isFetching ? t('taiga.sincronizando') : t('taiga.sincronizar')}
        </button>
      </div>

      {/* Estadísticas */}
      {data && data.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-indigo-400">
            <p className="text-xs text-gray-500 uppercase">{t('taiga.total')}</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{totalAll}</p>
            <p className="text-xs text-gray-400">{t('taiga.historias')}</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-green-400">
            <p className="text-xs text-gray-500 uppercase">{t('taiga.cerradas')}</p>
            <p className="text-2xl font-bold text-green-700 mt-1">{cerradasAll}</p>
            <p className="text-xs text-gray-400">{Math.round(cerradasAll / totalAll * 100)}% completado</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-amber-400">
            <p className="text-xs text-gray-500 uppercase">{t('taiga.abiertas')}</p>
            <p className="text-2xl font-bold text-amber-600 mt-1">{totalAll - cerradasAll}</p>
            <p className="text-xs text-gray-400">{t('taiga.historias')}</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border-l-4 border-purple-400">
            <p className="text-xs text-gray-500 uppercase">{t('taiga.puntos')}</p>
            <p className="text-2xl font-bold text-purple-700 mt-1">{puntosAll > 0 ? puntosAll : '—'}</p>
            <p className="text-xs text-gray-400">story points</p>
          </div>
        </div>
      )}

      {/* Filtros y búsqueda */}
      {data && data.length > 0 && (
        <div className="flex flex-col sm:flex-row gap-3 mb-5">
          {/* Búsqueda */}
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              className="w-full border rounded-lg pl-8 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              placeholder={t('taiga.buscar')}
              value={buscar}
              onChange={e => setBuscar(e.target.value)}
            />
          </div>

          {/* Filtro de estado */}
          <div className="flex rounded-lg border overflow-hidden text-sm">
            {(['all', 'open', 'closed'] as Filtro[]).map(f => (
              <button
                key={f}
                onClick={() => setFiltro(f)}
                className={`px-4 py-2 transition-colors ${
                  filtro === f
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                {f === 'all'    ? t('taiga.filtroTodo')     :
                 f === 'open'   ? t('taiga.filtroAbiertas') :
                                  t('taiga.filtroCerradas')}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Estado: cargando ─────────────────────────────────────────────── */}
      {isLoading && (
        <div className="flex items-center justify-center py-20 text-gray-400">
          <RefreshCw size={20} className="animate-spin mr-2" />
          <span className="text-sm">{t('common.loading')}</span>
        </div>
      )}

      {/* ── Estado: error ────────────────────────────────────────────────── */}
      {isError && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 text-center">
          <BookOpen size={32} className="text-amber-400 mx-auto mb-3" />
          <p className="text-sm font-medium text-amber-800 mb-1">
            {sinCredenciales ? t('taiga.noCredenciales') : t('taiga.noDisponible')}
          </p>
          <p className="text-xs text-amber-600 mt-1 font-mono break-all">{errMsg}</p>
          {sinCredenciales && (
            <p className="text-xs text-amber-600 mt-3">
              Configura <code className="bg-amber-100 px-1 rounded">TAIGA_USERNAME</code>,{' '}
              <code className="bg-amber-100 px-1 rounded">TAIGA_PASSWORD</code> y{' '}
              <code className="bg-amber-100 px-1 rounded">TAIGA_PROJECT_SLUG</code>{' '}
              como variables de entorno en Railway.
            </p>
          )}
        </div>
      )}

      {/* ── Estado: vacío después de filtro ──────────────────────────────── */}
      {!isLoading && !isError && data && historiasFiltradas.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <Search size={32} className="mx-auto mb-3 opacity-50" />
          <p className="text-sm">{t('common.noData')}</p>
        </div>
      )}

      {/* ── Lista agrupada por sprint ─────────────────────────────────────── */}
      {!isLoading && !isError && grupos.length > 0 && (
        <div>
          {grupos.map(([sprintKey, hs]) => (
            <SprintGroup
              key={sprintKey}
              nombre={sprintKey === '__backlog__' ? t('taiga.backlog') : sprintKey}
              historias={hs}
            />
          ))}

          {/* Link externo a Taiga */}
          <div className="text-center mt-4">
            <a
              href={`https://tree.taiga.io/project/cesar_camilo-greenhouse-manager/backlog`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-xs text-indigo-600 hover:text-indigo-800 hover:underline"
            >
              <ExternalLink size={12} />
              {t('taiga.verEnTaiga')}
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
