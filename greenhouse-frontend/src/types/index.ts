/*
 * GreenHouse Manager
 * Autores: [Nombres del equipo]
 * Fecha: 2026
 */

export interface TipoPlanta {
  id?: number
  nombre: string
  descripcion?: string
  temperaturaMin: number
  temperaturaMax: number
  humedadMin: number
  humedadMax: number
  cicloDias: number
  cuidadosEspeciales?: string
}

export interface Zona {
  id?: number
  nombre: string
  dimensionM2?: number
  capacidadMaxPlantas?: number
  estado: 'ACTIVA' | 'EN_MANTENIMIENTO' | 'INACTIVA'
  ubicacion?: string
}

export interface Planta {
  id?: number
  codigo: string
  tipoPlanta: { id: number; nombre?: string; cicloDias?: number }
  zona: { id: number; nombre?: string }
  fechaSiembra: string
  estado: 'SEMBRADA' | 'EN_CRECIMIENTO' | 'LISTA_PARA_COSECHAR' | 'COSECHADA' | 'MUERTA'
  observaciones?: string
}

export interface Empleado {
  id?: number
  nombreCompleto: string
  email: string
  passwordHash?: string
  rol: 'ADMINISTRADOR' | 'EMPLEADO' | 'SUPERVISOR'
  telefono?: string
  estado: 'ACTIVO' | 'INACTIVO'
  fechaIngreso?: string
}

export interface Sensor {
  id?: number
  codigo: string
  tipoSensor: 'TEMPERATURA' | 'HUMEDAD' | 'PH' | 'CO2' | 'LUZ'
  zona: { id: number; nombre?: string }
  estado: 'ACTIVO' | 'INACTIVO' | 'EN_MANTENIMIENTO'
  fechaInstalacion?: string
  umbralMin?: number
  umbralMax?: number
}

export interface LecturaSensor {
  id?: number
  sensor: { id: number; codigo?: string; tipoSensor?: string }
  valor: number
  unidad: string
  fechaHora?: string
  fuente: 'AUTOMATICA' | 'MANUAL'
}

export interface Alerta {
  id?: number
  tipo: string
  severidad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA'
  zona: Zona
  sensor?: Sensor
  fechaGeneracion: string
  estado: 'PENDIENTE' | 'ATENDIDA' | 'DESCARTADA'
  descripcion?: string
  notasResolucion?: string
  atendidoPor?: { id: number; nombreCompleto?: string }
}

export interface Cosecha {
  id?: number
  planta: { id: number; codigo?: string; tipoPlanta?: { nombre?: string } }
  empleado: { id: number; nombreCompleto?: string }
  fechaCosecha: string
  pesoKg: number
  calidad: 'A' | 'B' | 'C'
  destino: 'VENTA' | 'CONSUMO_INTERNO' | 'DESCARTE'
  observaciones?: string
}

export interface Tratamiento {
  id?: number
  planta: { id: number; codigo?: string }
  empleado: { id: number; nombreCompleto?: string }
  tipoTratamiento: 'FERTILIZACION' | 'PESTICIDA' | 'PODA' | 'RIEGO_MANUAL' | 'REVISION'
  productoUtilizado?: string
  dosis?: string
  fechaHora: string
  resultadoObservado?: string
}

export interface Turno {
  id?: number
  empleado: { id: number }
  zona: { id: number }
  fechaHoraInicio: string
  fechaHoraFin?: string
  actividadesRealizadas?: string
}
