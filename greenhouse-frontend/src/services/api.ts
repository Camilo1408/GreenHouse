/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import axios from 'axios'

/**
 * Instancia base de Axios configurada para el backend de GreenHouse Manager.
 *
 * En desarrollo utiliza el proxy de Vite (`/api` → `localhost:8080`).
 * En producción Railway usa `VITE_API_URL` como base URL.
 * Las credenciales de sesión (cookies) se incluyen en cada petición (`withCredentials: true`).
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

/**
 * Interceptor de respuesta global.
 * Redirige automáticamente a `/login` cuando el backend responde 401 (no autenticado),
 * excepto cuando el usuario ya se encuentra en páginas públicas (`/login`, `/register`).
 */
api.interceptors.response.use(
  res => res,
  err => {
    // Only redirect to /login when a 401 occurs outside of the login/register pages.
    // Without this guard, AuthContext's /auth/me check (which returns 401 when the
    // user is not yet logged in) would trigger a redirect that reloads the page
    // endlessly while the user is already on /login.
    const publicPaths = ['/login', '/register']
    const onPublicPage = publicPaths.some(p => window.location.pathname.startsWith(p))
    if (err.response?.status === 401 && !onPublicPage) {
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

/**
 * Servicio para operaciones CRUD sobre zonas del invernadero.
 * Corresponde a los endpoints `GET/POST/PUT/DELETE /api/zonas`.
 */
export const zonaService = {
  /** Retorna todas las zonas registradas. */
  getAll: () => api.get('/zonas'),
  /** Retorna una zona por su ID. */
  getById: (id: number) => api.get(`/zonas/${id}`),
  /** Crea una nueva zona. */
  create: (data: object) => api.post('/zonas', data),
  /** Actualiza una zona existente. */
  update: (id: number, data: object) => api.put(`/zonas/${id}`, data),
  /** Elimina una zona y todos sus datos dependientes. */
  delete: (id: number) => api.delete(`/zonas/${id}`),
}

/**
 * Servicio para operaciones CRUD sobre plantas del invernadero.
 * Corresponde a los endpoints `GET/POST/PUT/DELETE /api/plantas`.
 */
export const plantaService = {
  /** Retorna todas las plantas. */
  getAll: () => api.get('/plantas'),
  /** Retorna las plantas de una zona específica. */
  getByZona: (zonaId: number) => api.get(`/plantas/zona/${zonaId}`),
  /** Retorna las plantas con un estado específico. */
  getByEstado: (estado: string) => api.get(`/plantas/estado/${estado}`),
  /** Registra una nueva planta. */
  create: (data: object) => api.post('/plantas', data),
  /** Actualiza una planta existente. */
  update: (id: number, data: object) => api.put(`/plantas/${id}`, data),
  /** Elimina una planta junto con sus tratamientos y cosechas. */
  delete: (id: number) => api.delete(`/plantas/${id}`),
}

/**
 * Servicio para el catálogo de tipos de planta.
 * Corresponde a los endpoints `GET/POST/PUT/DELETE /api/tipos-planta`.
 */
export const tipoPlantaService = {
  /** Retorna todos los tipos de planta del catálogo. */
  getAll: () => api.get('/tipos-planta'),
  /** Retorna un tipo de planta por su ID. */
  getById: (id: number) => api.get(`/tipos-planta/${id}`),
  /** Crea un nuevo tipo de planta. */
  create: (data: object) => api.post('/tipos-planta', data),
  /** Actualiza un tipo de planta existente. */
  update: (id: number, data: object) => api.put(`/tipos-planta/${id}`, data),
  /** Elimina un tipo de planta del catálogo. */
  delete: (id: number) => api.delete(`/tipos-planta/${id}`),
}

/**
 * Servicio para operaciones CRUD sobre sensores del invernadero.
 * Corresponde a los endpoints `GET/POST/PUT/DELETE /api/sensores`.
 */
export const sensorService = {
  /** Retorna todos los sensores. */
  getAll: () => api.get('/sensores'),
  /** Retorna un sensor por su ID. */
  getById: (id: number) => api.get(`/sensores/${id}`),
  /** Retorna los sensores de una zona específica. */
  getByZona: (zonaId: number) => api.get(`/sensores/zona/${zonaId}`),
  /** Crea un nuevo sensor. */
  create: (data: object) => api.post('/sensores', data),
  /** Actualiza un sensor existente. */
  update: (id: number, data: object) => api.put(`/sensores/${id}`, data),
  /** Elimina un sensor junto con sus lecturas (las alertas se desvinculan). */
  delete: (id: number) => api.delete(`/sensores/${id}`),
}

/**
 * Servicio para consulta y gestión de alertas del invernadero.
 * Corresponde a los endpoints bajo `/api/alertas`.
 */
export const alertaService = {
  /** Retorna todas las alertas. */
  getAll: () => api.get('/alertas'),
  /** Retorna las alertas en estado PENDIENTE. */
  getPendientes: () => api.get('/alertas/pendientes'),
  /** Retorna el total de alertas en estado PENDIENTE. */
  countPendientes: () => api.get('/alertas/count/pendientes'),
  /** Retorna las alertas de una zona específica. */
  getByZona: (zonaId: number) => api.get(`/alertas/zona/${zonaId}`),
  /**
   * Crea una alerta manual reportada por un empleado o supervisor.
   * @param data - Datos de la alerta (zonaId, tipo, severidad, descripcion, empleadoId?)
   */
  crearManual: (data: {
    zonaId: number
    tipo: string
    severidad: string
    descripcion: string
    empleadoId?: number
  }) => api.post('/alertas', data),
  /**
   * Marca una alerta como atendida.
   * @param id - ID de la alerta
   * @param body - Notas de resolución y/o empleado responsable (opcional)
   */
  atender: (id: number, body?: { notas?: string; empleadoId?: number }) =>
    api.patch(`/alertas/${id}/atender`, body ?? {}),
  /**
   * Descarta una alerta.
   * @param id - ID de la alerta
   * @param body - Notas de descarte y/o empleado responsable (opcional)
   */
  descartar: (id: number, body?: { notas?: string; empleadoId?: number }) =>
    api.patch(`/alertas/${id}/descartar`, body ?? {}),
  /**
   * Agrega notas a una alerta en cualquier estado.
   * @param id - ID de la alerta
   * @param body - Notas y opcionalmente el empleado que las agrega
   */
  agregarNotas: (id: number, body: { notas: string; empleadoId?: number }) =>
    api.patch(`/alertas/${id}/notas`, body),
}

/**
 * Servicio para registro y consulta de lecturas de sensores.
 * Corresponde a los endpoints bajo `/api/lecturas`.
 */
export const lecturaService = {
  /** Retorna todas las lecturas de un sensor específico. */
  getBySensor: (sensorId: number) => api.get(`/lecturas/sensor/${sensorId}`),
  /** Retorna las lecturas de todos los sensores de una zona, ordenadas por fecha desc. */
  getByZona: (zonaId: number) => api.get(`/lecturas/zona/${zonaId}`),
  /**
   * Registra una nueva lectura. Si el valor está fuera de umbral, el backend genera una alerta automáticamente.
   * @param data - Datos de la lectura (sensor, valor, fechaHora?)
   */
  registrar: (data: object) => api.post('/lecturas', data),
}

/**
 * Servicio para registro y consulta de cosechas del invernadero.
 * Corresponde a los endpoints bajo `/api/cosechas`.
 */
export const cosechaService = {
  /** Retorna todas las cosechas registradas. */
  getAll: () => api.get('/cosechas'),
  /**
   * Retorna las cosechas dentro de un período de fechas.
   * @param inicio - Fecha de inicio en formato ISO (yyyy-MM-dd)
   * @param fin - Fecha de fin en formato ISO (yyyy-MM-dd)
   */
  getByPeriodo: (inicio: string, fin: string) =>
    api.get(`/cosechas/periodo?inicio=${inicio}&fin=${fin}`),
  /**
   * Retorna el total de kg cosechados en un mes específico.
   * @param year - Año (ej. 2026)
   * @param month - Mes (1–12)
   */
  totalKgMes: (year: number, month: number) =>
    api.get(`/cosechas/estadisticas/mes?year=${year}&month=${month}`),
  /**
   * Registra una nueva cosecha. Actualiza el estado de la planta a COSECHADA.
   * @param data - Datos de la cosecha (planta, empleado, fechaCosecha, pesoKg, calidad, destino)
   */
  registrar: (data: object) => api.post('/cosechas', data),
}

/**
 * Servicio para operaciones CRUD sobre empleados del invernadero.
 * Corresponde a los endpoints bajo `/api/empleados`.
 */
export const empleadoService = {
  /** Retorna todos los empleados (solo ADMINISTRADOR). */
  getAll: () => api.get('/empleados'),
  /** Retorna un empleado por su ID (solo ADMINISTRADOR). */
  getById: (id: number) => api.get(`/empleados/${id}`),
  /** Retorna el perfil del empleado autenticado, o `{sin_perfil: true}` si no tiene perfil. */
  getMe: () => api.get('/empleados/me'),
  /** Crea un nuevo empleado (solo ADMINISTRADOR). */
  create: (data: object) => api.post('/empleados', data),
  /** Actualiza un empleado existente (solo ADMINISTRADOR). */
  update: (id: number, data: object) => api.put(`/empleados/${id}`, data),
  /** Elimina un empleado (solo ADMINISTRADOR). */
  delete: (id: number) => api.delete(`/empleados/${id}`),
}

/**
 * Servicio para operaciones CRUD sobre tratamientos aplicados a las plantas.
 * Corresponde a los endpoints bajo `/api/tratamientos`.
 */
export const tratamientoService = {
  /** Retorna todos los tratamientos. */
  getAll: () => api.get('/tratamientos'),
  /** Retorna los tratamientos de una planta específica. */
  getByPlanta: (plantaId: number) => api.get(`/tratamientos/planta/${plantaId}`),
  /** Registra un nuevo tratamiento. */
  create: (data: object) => api.post('/tratamientos', data),
  /** Actualiza un tratamiento existente (requiere ADMINISTRADOR o SUPERVISOR). */
  update: (id: number, data: object) => api.put(`/tratamientos/${id}`, data),
  /** Elimina un tratamiento (solo ADMINISTRADOR). */
  delete: (id: number) => api.delete(`/tratamientos/${id}`),
}

/**
 * Servicio proxy para historias de usuario de Taiga.
 * Solo accesible para usuarios con rol ADMINISTRADOR.
 * Corresponde a los endpoints bajo `/api/taiga`.
 */
export const taigaService = {
  /**
   * Retorna todas las historias de usuario del proyecto Taiga.
   * El backend autentica con Taiga y cachea el token 23h.
   * Devuelve 503 si las credenciales no están configuradas o si Taiga no responde.
   */
  getHistorias: () => api.get('/taiga/historias'),
}

export default api
