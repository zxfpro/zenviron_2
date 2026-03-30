import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

function healthPlugin(): Plugin {
  return {
    name: 'local-health-endpoint',
    configureServer(server) {
      server.middlewares.use('/health', (_req, res) => {
        res.setHeader('Content-Type', 'application/json')
        res.end(
          JSON.stringify({
            status: 'ok',
            service: 'clean-frontend-v2-dev',
            version: '0.1.0',
            timestamp: new Date().toISOString()
          })
        )
      })
    }
  }
}

export default defineConfig({
  plugins: [react(), healthPlugin()],
  server: {
    host: '127.0.0.1',
    port: 3000
  }
})
