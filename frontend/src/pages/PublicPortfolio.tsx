import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getApiBaseUrl } from '../lib/auth'

export default function PublicPortfolio() {
	const { username } = useParams()
	const [data, setData] = useState<any>(null)
	const [error, setError] = useState<string | null>(null)

	useEffect(() => {
		const api = getApiBaseUrl()
		fetch(`${api}/api/portfolio/${username}`)
			.then(r => r.json())
			.then(setData)
			.catch(e => setError(String(e)))
	}, [username])

	if (error) return <div className="p-6 text-red-600">Erreur: {error}</div>
	if (!data) return <div className="p-6">Chargement…</div>

	return (
		<div className="min-h-screen bg-background text-foreground p-6 max-w-3xl mx-auto">
			<div className="flex items-center gap-4 mb-6">
				{data.user.avatar_url && <img src={data.user.avatar_url} alt="avatar" className="w-16 h-16 rounded-full" />}
				<div>
					<h1 className="text-2xl font-bold">{data.user.name || data.user.username}</h1>
					{data.settings.headline && <div className="opacity-80">{data.settings.headline}</div>}
					{data.settings.location && <div className="text-sm opacity-70">{data.settings.location}</div>}
				</div>
			</div>
			{data.user.bio && <p className="mb-4">{data.user.bio}</p>}
			{data.settings.skills?.length ? (
				<div className="mb-6">
					<h2 className="font-semibold mb-2">Compétences</h2>
					<div className="flex flex-wrap gap-2">
						{data.settings.skills.map((s: string, i: number) => (
							<span key={i} className="border rounded px-2 py-0.5 text-sm">{s}</span>
						))}
					</div>
				</div>
			) : null}
			<div>
				<h2 className="font-semibold mb-2">Projets</h2>
				<ul className="space-y-2">
					{data.projects.map((p: any) => (
						<li key={p.id} className="border rounded p-3">
							<div className="font-semibold">{p.title}</div>
							<div className="text-sm opacity-80">{p.description}</div>
							<div className="text-sm mt-1">Statut: {p.status} • Avancement: {p.progress_percent}%</div>
						</li>
					))}
				</ul>
			</div>
		</div>
	)
}

