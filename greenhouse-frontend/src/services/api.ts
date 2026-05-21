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

export const alertaService = {
  getAll: () => api.get('/alertas'),
  getPendientes: () => api.get('/alertas/pendientes'),
  countPendientes: () => api.get('/alertas/count/pendientes'),
  atender: (id: number) => api.patch(`/alertas/${id}/atender`),
  descartar: (id: number) => api.patch(`/alertas/${id}/descartar`),
}

export const lecturaService = {
  getBySensor: (sensorId: number) => api.get(`/lecturas/sensor/${sensorId}`),
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
  create: (data: object) => api.post('/empleados', data),
  update: (id: number, data: object) => api.put(`/empleados/${id}`, data),
  delete: (id: number) => api.delete(`/empleados/${id}`),
}

export default api
