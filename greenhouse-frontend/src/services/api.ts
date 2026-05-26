/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const zonaService = {
  getAll: () => api.get('/zonas'),
  getById: (id: number) => api.get(`/zonas/${id}`),
  create: (data: object) => api.post('/zonas', data),
  update: (id: number, data: object) => api.put(`/zonas/${id}`, data),
  delete: (id: number) => api.delete(`/zonas/${id}`),
}

export const plantaService = {
  getAll: () => api.get('/plantas'),
  getByZona: (zonaId: number) => api.get(`/plantas/zona/${zonaId}`),
  getByEstado: (estado: string) => api.get(`/plantas/estado/${estado}`),
  create: (data: object) => api.post('/plantas', data),
  update: (id: number, data: object) => api.put(`/plantas/${id}`, data),
  delete: (id: number) => api.delete(`/plantas/${id}`),
}

export const tipoPlantaService = {
  getAll: () => api.get('/tipos-planta'),
  getById: (id: number) => api.get(`/tipos-planta/${id}`),
  create: (data: object) => api.post('/tipos-planta', data),
  update: (id: number, data: object) => api.put(`/tipos-planta/${id}`, data),
  delete: (id: number) => api.delete(`/tipos-planta/${id}`),
}

export const sensorService = {
  getAll: () => api.get('/sensores'),
  getById: (id: number) => api.get(`/sensores/${id}`),
  getByZona: (zonaId: number) => api.get(`/sensores/zona/${zonaId}`),
  create: (data: object) => api.post('/sensores', data),
  update: (id: number, data: object) => api.put(`/sensores/${id}`, data),
  delete: (id: number) => api.delete(`/sensores/${id}`),
}

export const alertaService = {
  getAll: () => api.get('/alertas'),
  getPendientes: () => api.get('/alertas/pendientes'),
  countPendientes: () => api.get('/alertas/count/pendientes'),
  getByZona: (zonaId: number) => api.get(`/alertas/zona/${zonaId}`),
  crearManual: (data: {
    zonaId: number
    tipo: string
    severidad: string
    descripcion: string
    empleadoId?: number
  }) => api.post('/alertas', data),
  atender: (id: number, body?: { notas?: string; empleadoId?: number }) =>
    api.patch(`/alertas/${id}/atender`, body ?? {}),
  descartar: (id: number, body?: { notas?: string; empleadoId?: number }) =>
    api.patch(`/alertas/${id}/descartar`, body ?? {}),
  agregarNotas: (id: number, body: { notas: string; empleadoId?: number }) =>
    api.patch(`/alertas/${id}/notas`, body),
}

export const lecturaService = {
  getBySensor: (sensorId: number) => api.get(`/lecturas/sensor/${sensorId}`),
  getByZona: (zonaId: number) => api.get(`/lecturas/zona/${zonaId}`),
  registrar: (data: object) => api.post('/lecturas', data),
}

export const cosechaService = {
  getAll: () => api.get('/cosechas'),
  getByPeriodo: (inicio: string, fin: string) =>
    api.get(`/cosechas/periodo?inicio=${inicio}&fin=${fin}`),
  totalKgMes: (year: number, month: number) =>
    api.get(`/cosechas/estadisticas/mes?year=${year}&month=${month}`),
  registrar: (data: object) => api.post('/cosechas', data),
}

export const empleadoService = {
  getAll: () => api.get('/empleados'),
  getById: (id: number) => api.get(`/empleados/${id}`),
  getMe: () => api.get('/empleados/me'),
  create: (data: object) => api.post('/empleados', data),
  update: (id: number, data: object) => api.put(`/empleados/${id}`, data),
  delete: (id: number) => api.delete(`/empleados/${id}`),
}

export const tratamientoService = {
  getAll: () => api.get('/tratamientos'),
  getByPlanta: (plantaId: number) => api.get(`/tratamientos/planta/${plantaId}`),
  create: (data: object) => api.post('/tratamientos', data),
  update: (id: number, data: object) => api.put(`/tratamientos/${id}`, data),
  delete: (id: number) => api.delete(`/tratamientos/${id}`),
}

export default api
