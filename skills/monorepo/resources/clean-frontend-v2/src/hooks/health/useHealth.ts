import { useCallback, useEffect, useState } from 'react'
import { fetchHealth } from '../../api/health/health.api'
import { toHealthViewModel, type HealthViewModel } from '../../models/health/health.model'

interface UseHealthResult {
  data: HealthViewModel | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export function useHealth(): UseHealthResult {
  const [data, setData] = useState<HealthViewModel | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    const controller = new AbortController()
    setLoading(true)
    setError(null)

    try {
      const response = await fetchHealth(controller.signal)
      setData(toHealthViewModel(response))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown health check error'
      setError(message)
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { data, loading, error, refresh }
}
