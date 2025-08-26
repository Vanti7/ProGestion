import type PlatformApi from './index'

const storage: PlatformApi['storage'] = {
	async getItem(key) {
		const raw = localStorage.getItem(key)
		if (raw == null) return null
		try { return JSON.parse(raw) } catch { return null }
	},
	async setItem(key, value) {
		localStorage.setItem(key, JSON.stringify(value))
	},
	async removeItem(key) {
		localStorage.removeItem(key)
	},
}

const fs: PlatformApi['fs'] = {
	async readText() {
		throw new Error('readText non supporté en Web sans File System Access API')
	},
	async writeText() {
		throw new Error('writeText non supporté en Web sans File System Access API')
	},
	async chooseOpenFile() { return null },
	async chooseSaveFile() { return null },
}

const api: PlatformApi = { fs, storage }
export default api

