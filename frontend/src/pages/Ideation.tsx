import { useEffect, useState } from 'react'
import { apiFetch, getApiBaseUrl } from '../lib/auth'

type Project = { id: number; title: string }

export default function Ideation() {
	const [projects, setProjects] = useState<Project[]>([])
	const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
	const [idea, setIdea] = useState('')
	const [raw, setRaw] = useState('')
	const [template, setTemplate] = useState('')
	const [roadmap, setRoadmap] = useState('')
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)

	useEffect(() => {
		(async () => {
			try {
				const api = getApiBaseUrl()
				const r = await apiFetch(`${api}/api/ai/template`)
				if (r.ok) {
					const data = await r.json()
					setTemplate(data.template || '')
				}
				const pr = await apiFetch(`${api}/api/projects`)
				if (pr.ok) {
					const list: Project[] = await pr.json()
					setProjects(list)
					if (list.length) setSelectedProjectId(list[0].id)
				}
			} catch {}
		})()
	}, [])

	async function generate() {
		setLoading(true)
		setError(null)
		try {
			const api = getApiBaseUrl()
			const res = await apiFetch(`${api}/api/ai/generate-roadmap`, {
				method: 'POST',
				body: JSON.stringify({ mode: 'skeleton', idea })
			})
			if (!res.ok) throw new Error('Échec génération')
			const data = await res.json()
			setRoadmap(data.roadmap)
		} catch (e: any) {
			setError(e.message || String(e))
		} finally {
			setLoading(false)
		}
	}

	async function reformat() {
		setLoading(true)
		setError(null)
		try {
			const api = getApiBaseUrl()
			const res = await apiFetch(`${api}/api/ai/generate-roadmap`, {
				method: 'POST',
				body: JSON.stringify({ mode: 'reformat', raw })
			})
			if (!res.ok) throw new Error('Échec reformatage')
			const data = await res.json()
			setRoadmap(data.roadmap)
		} catch (e: any) {
			setError(e.message || String(e))
		} finally {
			setLoading(false)
		}
	}

	async function importRoadmap() {
		if (!selectedProjectId) return
		if (!roadmap.trim()) {
			setError('Aucune roadmap à importer')
			return
		}
		setLoading(true)
		setError(null)
		try {
			const api = getApiBaseUrl()
			const res = await apiFetch(`${api}/api/tasks/import-roadmap`, {
				method: 'POST',
				body: JSON.stringify({ project_id: selectedProjectId, markdown: roadmap })
			})
			if (!res.ok) throw new Error('Échec import tâches')
		} catch (e: any) {
			setError(e.message || String(e))
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="p-6 space-y-6">
			<h2 className="text-xl font-bold">Idéation IA</h2>

			<div className="flex items-center gap-2">
				<label className="text-sm">Projet cible</label>
				<select className="border rounded px-2 py-1 text-black" value={selectedProjectId ?? ''} onChange={e => setSelectedProjectId(Number(e.target.value))}>
					{projects.map(p => (<option key={p.id} value={p.id}>{p.title}</option>))}
				</select>
			</div>

			<div className="space-y-2">
				<div className="flex items-center justify-between">
					<label className="block text-sm">Décrivez votre idée de projet (mode squelette)</label>
					{template && <button className="text-sm underline" onClick={() => setRaw(template)}>Insérer modèle</button>}
				</div>
				<textarea className="border rounded w-full min-h-[120px] text-black p-2" value={idea} onChange={e => setIdea(e.target.value)} />
				<button className="bg-black text-white px-3 py-1 rounded" onClick={generate} disabled={loading || !idea.trim()}>
					{loading ? 'Génération…' : 'Générer la roadmap (squelette)'}
				</button>
			</div>

			<div className="space-y-2">
				<label className="block text-sm">Texte libre à reformater (collez n’importe quel plan/roadmap)</label>
				<textarea className="border rounded w-full min-h-[120px] text-black p-2" value={raw} onChange={e => setRaw(e.target.value)} />
				<div className="flex gap-2">
					<button className="border px-3 py-1 rounded" onClick={() => setRaw(template)} disabled={!template}>Charger le modèle</button>
					<button className="bg-black text-white px-3 py-1 rounded" onClick={reformat} disabled={loading || !raw.trim()}>
						{loading ? 'Reformatage…' : 'Reformater au bon format'}
					</button>
				</div>
			</div>

			{error && <div className="text-red-600">Erreur: {error}</div>}
			{roadmap && (
				<div className="space-y-2">
					<h3 className="font-semibold mb-2">Résultat</h3>
					<pre className="whitespace-pre-wrap border rounded p-3 bg-white text-black">{roadmap}</pre>
					<div className="flex gap-2">
						<button className="border px-3 py-1 rounded" onClick={() => navigator.clipboard.writeText(roadmap)}>Copier</button>
						<button className="bg-black text-white px-3 py-1 rounded" onClick={importRoadmap} disabled={!selectedProjectId || loading}>Créer les tâches dans le projet</button>
					</div>
				</div>
			)}
		</div>
	)
}


