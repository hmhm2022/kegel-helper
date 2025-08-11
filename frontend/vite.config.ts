import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  resolve: {
    alias: {
      '@': resolve('./src'),
      // 只在开发环境中使用mock，生产环境使用真实的Tauri API
      ...(process.env.NODE_ENV === 'development' && !process.env.TAURI_PLATFORM ? {
        '@tauri-apps/api': resolve('./src/mock/@tauri-apps/api'),
      } : {}),
    },
  },
  define: {
    // 确保在Tauri环境中正确设置__TAURI__全局变量
    __TAURI__: JSON.stringify(process.env.TAURI_PLATFORM !== undefined || process.env.NODE_ENV === 'production'),
  },
  server: {
    port: 3000,
    host: '127.0.0.1',
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
