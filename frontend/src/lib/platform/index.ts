export interface FileSystemApi {
	readText(filePath: string): Promise<string>
	writeText(filePath: string, contents: string): Promise<void>
	chooseOpenFile(accept?: string[]): Promise<string | null>
	chooseSaveFile(suggestedName?: string): Promise<string | null>
}

export interface StorageApi {
	getItem<T = unknown>(key: string): Promise<T | null>
	setItem<T = unknown>(key: string, value: T): Promise<void>
	removeItem(key: string): Promise<void>
}

export interface PlatformApi {
	fs: FileSystemApi
	storage: StorageApi
}

export type { PlatformApi as default }

