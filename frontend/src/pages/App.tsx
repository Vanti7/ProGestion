import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch, clearToken, getApiBaseUrl, getToken, setToken } from '../lib/auth'

type Project = {
	id: number
	title: string
	description?: string | null
	status: string
	progress_percent: number
	priority: string
	owner_id: number
}

export default function App() {
	const [projects, setProjects] = useState<Project[]>([])
	const [error, setError] = useState<string | null>(null)
	const [me, setMe] = useState<{ email: string; username: string | null } | null>(null)
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')

	useEffect(() => {
		const apiBase = getApiBaseUrl()
		fetch(`${apiBase}/api/projects`)
			.then(r => r.json())
			.then(setProjects)
			.catch(e => setError(String(e)))

		if (getToken()) {
			apiFetch(`${apiBase}/api/auth/me`).then(async r => {
				if (r.ok) setMe(await r.json())
			})
		}
	}, [])

	async function handleLogin(e: React.FormEvent) {
		e.preventDefault()
		setError(null)
		try {
			const apiBase = getApiBaseUrl()
			const res = await fetch(`${apiBase}/api/auth/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, password }),
			})
			if (!res.ok) throw new Error('Identifiants invalides')
			const data = await res.json()
			setToken(data.access_token)
			const meRes = await apiFetch(`${apiBase}/api/auth/me`)
			if (meRes.ok) setMe(await meRes.json())
		} catch (err: any) {
			setError(err.message || String(err))
		}
	}

	function logout() {
		clearToken()
		setMe(null)
	}

	const apiBase = getApiBaseUrl()
	return (
		<div className="min-h-screen bg-background text-foreground p-6">
			<div className="flex items-center justify-between mb-4">
				<h1 className="text-2xl font-bold">Project Portfolio</h1>
				{me ? (
					<div className="flex items-center gap-3">
						<span className="text-sm opacity-80">Connecté: {me.email}</span>
						<Link to="/dashboard" className="text-sm underline">Dashboard</Link>
						<Link to="/ideation" className="text-sm underline">Idéation IA</Link>
						<button className="text-sm underline" onClick={logout}>Se déconnecter</button>
					</div>
				) : null}
			</div>

			{!me && (
				<div className="mb-6 space-y-3">
					<form onSubmit={handleLogin} className="flex gap-2 items-end flex-wrap">
						<div>
							<label className="block text-sm mb-1">Email</label>
							<input className="border rounded px-2 py-1 text-black" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
						</div>
						<div>
							<label className="block text-sm mb-1">Mot de passe</label>
							<input className="border rounded px-2 py-1 text-black" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
						</div>
						<button className="bg-black text-white px-3 py-1 rounded" type="submit">Se connecter</button>
					</form>
					<div className="flex gap-3">
						<a className="underline" href={`${apiBase}/api/auth/oauth/github`}>Se connecter avec GitHub</a>
						<a className="underline" href={`${apiBase}/api/auth/oauth/gitlab`}>Se connecter avec GitLab</a>
					</div>
				</div>
			)}

			{error && <div className="text-red-600">Erreur: {error}</div>}
			<ul className="space-y-2">
				{projects.map(p => (
					<li key={p.id} className="border rounded p-3">
						<div className="font-semibold">{p.title}</div>
						<div className="text-sm opacity-80">{p.description}</div>
						<div className="text-sm mt-1">Statut: {p.status} • Priorité: {p.priority} • Avancement: {p.progress_percent}%</div>
					</li>
				))}
			</ul>
		</div>
	)
}

