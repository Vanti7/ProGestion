import type PlatformApi from './index'
import { open as dialogOpen, save as dialogSave } from '@tauri-apps/api/dialog'
import { readTextFile, writeTextFile } from '@tauri-apps/api/fs'

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
	async readText(filePath: string) {
		return readTextFile(filePath)
	},
	async writeText(filePath: string, contents: string) {
		return writeTextFile({ path: filePath, contents })
	},
	async chooseOpenFile(accept?: string[]) {
		const selected = await dialogOpen({ filters: accept ? [{ name: 'files', extensions: accept.map(x => x.replace(/^\./, '')) }] : undefined })
		if (!selected || Array.isArray(selected)) return null
		return selected
	},
	async chooseSaveFile(suggestedName?: string) {
		const file = await dialogSave({ defaultPath: suggestedName })
		return file || null
	},
}

const api: PlatformApi = { fs, storage }
export default api

