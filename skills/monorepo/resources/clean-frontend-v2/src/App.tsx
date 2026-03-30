import { useHealth } from './hooks/health/useHealth'

const featureList = [
  'React 18 + TypeScript 5',
  'Vite 5 fast dev/build',
  'Strict type-check defaults',
  'Docker + Nginx production deployment'
]

export default function App() {
  const { data, loading, error, refresh } = useHealth()

  return (
    <main className="page">
      <section className="card">
        <p className="badge">Starter</p>
        <h1>Clean Frontend V2</h1>
        <p className="desc">A clean baseline to start new frontend projects.</p>

        <div className="health-block">
          <div className="health-row">
            <span className="health-title">Health</span>
            <button className="refresh-btn" type="button" onClick={() => void refresh()}>
              Refresh
            </button>
          </div>

          {loading && <p className="health-loading">Checking...</p>}
          {error && <p className="health-error">Unavailable: {error}</p>}
          {data && (
            <p className="health-ok">
              {data.isHealthy ? 'OK' : 'NOT OK'} · {data.serviceName} · {data.version} · {data.checkedAt}
            </p>
          )}
        </div>

        <ul>
          {featureList.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </main>
  )
}
