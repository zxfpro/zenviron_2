import type { HealthResponse } from '../../types/api/health'

export interface HealthViewModel {
  isHealthy: boolean
  serviceName: string
  version: string
  checkedAt: string
}

export function toHealthViewModel(data: HealthResponse): HealthViewModel {
  return {
    isHealthy: data.status === 'ok',
    serviceName: data.service,
    version: data.version,
    checkedAt: new Date(data.timestamp).toLocaleString()
  }
}
