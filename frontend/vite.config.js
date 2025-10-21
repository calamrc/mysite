import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Get API base URL from environment (for production) or use default for development
const apiTarget = process.env.VITE_API_BASE_URL || 'http://localhost:5000'

export default defineConfig({
  plugins: [vue()],
  root: '.',
  publicDir: 'public',
  server: {
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
        secure: apiTarget.startsWith('https'),
        // In CSR architecture, credentials need to be handled manually
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        }
      }
    }
  },
  build: {
    // Build to static folder for Flask serving (single server approach)
    outDir: '../static',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: 'index.html'
      }
    }
  },
  // Define environment variables available in the frontend
  define: {
    __VUE_PROD_DEVTOOLS__: false,
  }
})
