import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => ({
	plugins: [react()],
	server: {
		port: 5173,
		host: true,
	},
	resolve: {
		alias: {
			platform: mode === 'desktop'
				? path.resolve(__dirname, 'src/lib/platform/desktop.ts')
				: path.resolve(__dirname, 'src/lib/platform/web.ts'),
		},
	},
}))

