const TOKEN_KEY = 'jwt_token'

export function getApiBaseUrl(): string {
	return import.meta.env.VITE_API_URL || 'http://localhost:5000'
}

export function getToken(): string | null {
	return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
	localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
	localStorage.removeItem(TOKEN_KEY)
}

export async function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
	const token = getToken()
	const headers = new Headers(init.headers)
	if (token) headers.set('Authorization', `Bearer ${token}`)
	if (!headers.has('Content-Type') && init.body) headers.set('Content-Type', 'application/json')
	return fetch(input, { ...init, headers })
}

export function isAuthenticated(): boolean {
	return Boolean(getToken())
}

