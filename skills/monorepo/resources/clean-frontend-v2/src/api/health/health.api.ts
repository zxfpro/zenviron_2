import type { HealthResponse } from '../../types/api/health'

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch('/health', {
    method: 'GET',
    headers: { Accept: 'application/json' },
    signal
  })

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`)
  }

  const data = (await response.json()) as HealthResponse
  return data
}
