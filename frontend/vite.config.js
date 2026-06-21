import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

const portConflictPlugin = () => ({
  name: 'port-conflict-handler',
  configureServer(server) {
    server.httpServer?.on('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        console.error('\n========================================')
        console.error('  端口冲突错误！')
        console.error('========================================')
        console.error('  端口 5173 已被占用，请执行以下操作：')
        console.error()
        console.error('  1. 关闭占用端口的程序，或')
        console.error('  2. 修改 vite.config.js 中的 port 为其他可用端口')
        console.error()
        console.error('  查找占用进程：lsof -ti:5173 | xargs kill -9')
        console.error('========================================\n')
        process.exit(1)
      }
    })
  }
})

export default defineConfig({
  plugins: [vue(), portConflictPlugin()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
})
