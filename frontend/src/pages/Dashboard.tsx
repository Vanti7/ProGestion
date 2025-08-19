import { useEffect, useState } from 'react'
import { apiFetch, getApiBaseUrl } from '../lib/auth'

type Project = {
	id: number
	title: string
	description?: string | null
	roadmap_path?: string | null
}

export default function Dashboard() {
	const [me, setMe] = useState<{ email: string } | null>(null)
	const [projects, setProjects] = useState<Project[]>([])
	const [tasks, setTasks] = useState<any[]>([])
	const [columns, setColumns] = useState<any[]>([])
	const [newColumnName, setNewColumnName] = useState('')
	const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
	const [newTaskTitle, setNewTaskTitle] = useState('')
	const [editingId, setEditingId] = useState<number | null>(null)
	const [editTitle, setEditTitle] = useState('')
	const [editDescription, setEditDescription] = useState('')
	const [error, setError] = useState<string | null>(null)
	const [portfolio, setPortfolio] = useState<any>(null)
	const [ghRepos, setGhRepos] = useState<any[]>([])
	const [ghSelected, setGhSelected] = useState<Record<string, boolean>>({})
	const [roadmapPath, setRoadmapPath] = useState('')
	const [detecting, setDetecting] = useState(false)
	const [candidates, setCandidates] = useState<string[]>([])

	useEffect(() => {
		const api = getApiBaseUrl()
		apiFetch(`${api}/api/auth/me`).then(async r => {
			if (r.ok) setMe(await r.json())
		}).catch(e => setError(String(e)))
		apiFetch(`${api}/api/projects`).then(async r => {
			if (r.ok) {
				const list: Project[] = await r.json()
				setProjects(list)
				if (list.length) setSelectedProjectId(list[0].id)
				if (list.length) setRoadmapPath(list[0].roadmap_path || '')
			}
		}).catch(e => setError(String(e)))
		apiFetch(`${api}/api/portfolio/me`).then(async r => { if (r.ok) setPortfolio(await r.json()) })
	}, [])

	useEffect(() => {
		if (selectedProjectId) {
			const p = projects.find(pr => pr.id === selectedProjectId)
			setRoadmapPath(p?.roadmap_path || '')
		}
	}, [selectedProjectId, projects])

	async function detectRoadmap() {
		if (!selectedProjectId) return
		setDetecting(true)
		try {
			const api = getApiBaseUrl()
			const r = await apiFetch(`${api}/api/projects/${selectedProjectId}/detect-roadmap`)
			if (r.ok) {
				const data = await r.json()
				setCandidates(data.candidates || [])
				if ((data.candidates || []).length === 1) setRoadmapPath(data.candidates[0])
			}
		} finally {
			setDetecting(false)
		}
	}

	async function saveRoadmapPath() {
		if (!selectedProjectId) return
		const api = getApiBaseUrl()
		await apiFetch(`${api}/api/projects/${selectedProjectId}`, { method: 'PUT', body: JSON.stringify({ roadmap_path: roadmapPath }) })
		const r = await apiFetch(`${api}/api/projects`)
		if (r.ok) setProjects(await r.json())
	}

	async function loadGithubRepos() {
		const api = getApiBaseUrl()
		const r = await apiFetch(`${api}/api/portfolio/me/github/repos`)
		if (r.ok) {
			const list = await r.json()
			setGhRepos(list)
			const sel: Record<string, boolean> = {}
			for (const row of portfolio?.public_repos || []) sel[row.full_name] = true
			setGhSelected(sel)
		}
	}

	async function saveGithubSelection() {
		const api = getApiBaseUrl()
		const body = ghRepos.filter(r => ghSelected[r.full_name])
		await apiFetch(`${api}/api/portfolio/me/github/publish`, { method: 'POST', body: JSON.stringify({ repos: body }) })
		const me = await apiFetch(`${api}/api/portfolio/me`)
		if (me.ok) setPortfolio(await me.json())
	}

	useEffect(() => {
		const api = getApiBaseUrl()
		if (selectedProjectId) {
			Promise.all([
				apiFetch(`${api}/api/tasks?project_id=${selectedProjectId}`),
				apiFetch(`${api}/api/kanban/board?project_id=${selectedProjectId}`)
			]).then(async ([tr, br]) => {
				if (tr.ok) setTasks(await tr.json())
				if (br.ok) {
					const b = await br.json()
					setColumns(b.columns || [])
				}
			})
		}
	}, [selectedProjectId])

	async function addTask(e: React.FormEvent) {
		e.preventDefault()
		if (!newTaskTitle || !selectedProjectId) return
		const api = getApiBaseUrl()
		const body: any = { title: newTaskTitle, project_id: selectedProjectId }
		if (columns.length) body.kanban_column_id = columns[0].id
		const res = await apiFetch(`${api}/api/tasks`, {
			method: 'POST',
			body: JSON.stringify(body)
		})
		if (res.ok) {
			setNewTaskTitle('')
			const list = await apiFetch(`${api}/api/tasks?project_id=${selectedProjectId}`)
			if (list.ok) setTasks(await list.json())
		}
	}

	async function createColumn() {
		if (!newColumnName.trim() || !selectedProjectId) return
		const api = getApiBaseUrl()
		const r = await apiFetch(`${api}/api/kanban/columns`, { method: 'POST', body: JSON.stringify({ project_id: selectedProjectId, name: newColumnName.trim() }) })
		if (r.ok) {
			setNewColumnName('')
			const br = await apiFetch(`${api}/api/kanban/board?project_id=${selectedProjectId}`)
			if (br.ok) setColumns((await br.json()).columns || [])
		}
	}

	async function deleteColumn(columnId: number) {
		const api = getApiBaseUrl()
		await apiFetch(`${api}/api/kanban/columns/${columnId}`, { method: 'DELETE' })
		const br = await apiFetch(`${api}/api/kanban/board?project_id=${selectedProjectId}`)
		if (br.ok) setColumns((await br.json()).columns || [])
	}

	function reorder<T>(arr: T[], fromIndex: number, toIndex: number): T[] {
		const copy = arr.slice()
		const [moved] = copy.splice(fromIndex, 1)
		copy.splice(toIndex, 0, moved)
		return copy
	}

	async function persistColumnOrder(cols: any[]) {
		const api = getApiBaseUrl()
		await Promise.all(cols.map((c, idx) => apiFetch(`${api}/api/kanban/columns/${c.id}`, { method: 'PUT', body: JSON.stringify({ order_index: idx }) })))
	}

	function onColumnDragStart(e: React.DragEvent, fromIndex: number) {
		e.dataTransfer.setData('text/column', String(fromIndex))
	}

	function onColumnDragOver(e: React.DragEvent) {
		e.preventDefault()
	}

	async function onColumnDrop(e: React.DragEvent, toIndex: number) {
		e.preventDefault()
		const fromIdxStr = e.dataTransfer.getData('text/column')
		if (fromIdxStr) {
			const fromIdx = Number(fromIdxStr)
			if (Number.isFinite(fromIdx) && fromIdx !== toIndex) {
				const newCols = reorder(columns, fromIdx, toIndex)
				setColumns(newCols)
				await persistColumnOrder(newCols)
			}
		}
	}

	async function updateTaskStatus(id: number, status: string) {
		const api = getApiBaseUrl()
		await apiFetch(`${api}/api/tasks/${id}`, { method: 'PUT', body: JSON.stringify({ status }) })
		const list = await apiFetch(`${api}/api/tasks?project_id=${selectedProjectId}`)
		if (list.ok) setTasks(await list.json())
	}

	function startEdit(t: any) {
		setEditingId(t.id)
		setEditTitle(t.title || '')
		setEditDescription(t.description || '')
	}

	function cancelEdit() {
		setEditingId(null)
		setEditTitle('')
		setEditDescription('')
	}

	async function saveEdit() {
		if (!editingId) return
		const api = getApiBaseUrl()
		await apiFetch(`${api}/api/tasks/${editingId}`, { method: 'PUT', body: JSON.stringify({ title: editTitle, description: editDescription }) })
		cancelEdit()
		const list = await apiFetch(`${api}/api/tasks?project_id=${selectedProjectId}`)
		if (list.ok) setTasks(await list.json())
	}

	async function deleteTask(id: number) {
		const api = getApiBaseUrl()
		await apiFetch(`${api}/api/tasks/${id}`, { method: 'DELETE' })
		const list = await apiFetch(`${api}/api/tasks?project_id=${selectedProjectId}`)
		if (list.ok) setTasks(await list.json())
	}

	function onDragStart(e: React.DragEvent, id: number) {
		e.dataTransfer.setData('text/plain', String(id))
	}

	function onDragOver(e: React.DragEvent) {
		e.preventDefault()
	}

	async function onDrop(e: React.DragEvent, newStatusOrColumnId: string | number) {
		e.preventDefault()
		const idStr = e.dataTransfer.getData('text/plain')
		const id = Number(idStr)
		if (!Number.isFinite(id)) return
		if (typeof newStatusOrColumnId === 'number') {
			const api = getApiBaseUrl()
			await apiFetch(`${api}/api/tasks/${id}`, { method: 'PUT', body: JSON.stringify({ kanban_column_id: newStatusOrColumnId }) })
			const list = await apiFetch(`${api}/api/tasks?project_id=${selectedProjectId}`)
			if (list.ok) setTasks(await list.json())
		} else {
			await updateTaskStatus(id, newStatusOrColumnId)
		}
	}

	async function syncRoadmap() {
		if (!selectedProjectId) return
		const api = getApiBaseUrl()
		const r = await apiFetch(`${api}/api/tasks/smart-sync?project_id=${selectedProjectId}`, { method: 'POST' })
		if (r.status === 404) {
			window.location.href = '/ideation'
			return
		}
		const list = await apiFetch(`${api}/api/tasks?project_id=${selectedProjectId}`)
		if (list.ok) setTasks(await list.json())
	}

	return (
		<div className="p-6">
			<h2 className="text-xl font-bold mb-4">Dashboard</h2>
			{error && <div className="text-red-600">Erreur: {error}</div>}
			{me && <div className="mb-4">Bienvenue, {me.email}</div>}
			<h3 className="font-semibold mb-2">Vos projets</h3>
			{portfolio?.user?.username && (
				<div className="mb-2 text-sm">
					Portfolio public: <a className="underline" href={`/user/${portfolio.user.username}`} target="_blank">/user/{portfolio.user.username}</a>
				</div>
			)}
			<div className="mb-4 flex gap-2 items-center flex-wrap">
				<label>Sélection:</label>
				<select className="border rounded px-2 py-1 text-black" value={selectedProjectId ?? ''} onChange={e => setSelectedProjectId(Number(e.target.value))}>
					{projects.map(p => (
						<option key={p.id} value={p.id}>{p.title}</option>
					))}
				</select>
				<button className="bg-black text-white px-3 py-1 rounded" onClick={syncRoadmap}>Importer roadmap</button>
				<button className="border px-3 py-1 rounded" onClick={() => (window.location.href = '/ideation')}>Aller à Idéation</button>
			</div>

			<div className="mb-4 flex gap-2 items-end">
				<div className="flex-1">
					<label className="block text-sm mb-1">Chemin du fichier roadmap pour ce projet</label>
					<input className="border rounded px-2 py-1 text-black w-full" placeholder="/home/…/mon-projet/roadmap.md" value={roadmapPath} onChange={e => setRoadmapPath(e.target.value)} />
					{candidates.length > 1 && (
						<select className="border rounded px-2 py-1 text-black w-full mt-2" value={roadmapPath} onChange={e => setRoadmapPath(e.target.value)}>
							<option value="">— Sélectionner un candidat détecté —</option>
							{candidates.map(c => (<option key={c} value={c}>{c}</option>))}
						</select>
					)}
				</div>
				<button className="border px-3 py-1 rounded" type="button" onClick={detectRoadmap} disabled={detecting}>{detecting ? 'Détection…' : 'Détecter'}</button>
				<button className="border px-3 py-1 rounded" type="button" onClick={saveRoadmapPath}>Enregistrer</button>
			</div>

			<div className="mb-8">
				<h3 className="font-semibold mb-2">Dépôts GitHub publics</h3>
				<div className="flex gap-2 mb-2">
					<button className="bg-black text-white px-3 py-1 rounded" onClick={loadGithubRepos}>Charger mes dépôts</button>
					<button className="border px-3 py-1 rounded" onClick={saveGithubSelection}>Enregistrer la sélection</button>
				</div>
				<ul className="space-y-2 max-h-64 overflow-auto border rounded p-2 bg-white text-black">
					{ghRepos.map(r => (
						<li key={r.full_name} className="flex items-start gap-2">
							<input type="checkbox" checked={Boolean(ghSelected[r.full_name])} onChange={e => setGhSelected(prev => ({ ...prev, [r.full_name]: e.target.checked }))} />
							<div>
								<div className="font-semibold">{r.full_name}</div>
								<div className="text-sm opacity-80">{r.description}</div>
								<div className="text-xs opacity-70">{r.language} • ⭐ {r.stargazers_count}</div>
							</div>
						</li>
					))}
				</ul>
			</div>

			<div className="mb-6">
				<form onSubmit={addTask} className="flex gap-2">
					<input className="border rounded px-2 py-1 text-black flex-1" placeholder="Nouvelle tâche" value={newTaskTitle} onChange={e => setNewTaskTitle(e.target.value)} />
					<button className="bg-black text-white px-3 py-1 rounded" type="submit">Ajouter</button>
				</form>
			</div>

			<div className="mb-6">
				<div className="flex gap-2 items.end">
					<div className="flex-1">
						<label className="block text-sm mb-1">Nouvelle colonne</label>
						<input className="border rounded px-2 py-1 text-black w-full" placeholder="Nom de colonne" value={newColumnName} onChange={e => setNewColumnName(e.target.value)} />
					</div>
					<button className="border px-3 py-1 rounded" onClick={createColumn} type="button">Ajouter la colonne</button>
				</div>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				{columns.length ? (
					columns.map((col, index) => (
						<div key={col.id} onDragOver={(e) => { onDragOver(e); onColumnDragOver(e) }} onDrop={(e) => onColumnDrop(e, index)} draggable onDragStart={(e) => onColumnDragStart(e, index)}>
							<h4 className="font-semibold mb-2">{col.name}</h4>
							<div className="text-xs opacity-70 mb-2 flex gap-2">
								<button className="underline" onClick={() => deleteColumn(col.id)}>Supprimer</button>
							</div>
							<ul className="space-y-2">
								{tasks.filter(t => t.kanban_column_id === col.id).map(t => (
									<li key={t.id} className="border rounded p-3" draggable onDragStart={(e) => onDragStart(e, t.id)}>
										<div className="font-semibold">{t.title}</div>
										<div className="text-sm opacity-80">{t.description}</div>
										<div className="text-sm mt-1">Priorité: {t.priority}</div>
										<div className="mt-2 flex gap-2">
											<button className="text-sm underline" onClick={() => startEdit(t)}>Éditer</button>
											<button className="text-sm underline text-red-600" onClick={() => deleteTask(t.id)}>Supprimer</button>
										</div>
										{editingId === t.id && (
											<div className="space-y-2 mt-2">
												<input className="border rounded px-2 py-1 text-black w-full" value={editTitle} onChange={e => setEditTitle(e.target.value)} />
												<textarea className="border rounded px-2 py-1 text-black w.full" value={editDescription} onChange={e => setEditDescription(e.target.value)} />
												<div className="flex gap-2">
													<button className="text-sm underline" onClick={saveEdit}>Enregistrer</button>
													<button className="text-sm underline" onClick={cancelEdit}>Annuler</button>
												</div>
											</div>
										)}
									</li>
								))}
							</ul>
						</div>
					))
				) : (
					<>
						<div onDragOver={onDragOver} onDrop={(e) => onDrop(e, 'todo')}>
					<h4 className="font-semibold mb-2">À faire</h4>
					<ul className="space-y-2">
						{tasks.filter(t => t.status === 'todo').map(t => (
							<li key={t.id} className="border rounded p-3" draggable onDragStart={(e) => onDragStart(e, t.id)}>
								{editingId === t.id ? (
									<div className="space-y-2">
										<input className="border rounded px-2 py-1 text-black w-full" value={editTitle} onChange={e => setEditTitle(e.target.value)} />
										<textarea className="border rounded px-2 py-1 text-black w.full" value={editDescription} onChange={e => setEditDescription(e.target.value)} />
										<div className="flex gap-2">
											<button className="text-sm underline" onClick={saveEdit}>Enregistrer</button>
											<button className="text-sm underline" onClick={cancelEdit}>Annuler</button>
										</div>
									</div>
								) : (
									<>
										<div className="font-semibold">{t.title}</div>
										<div className="text-sm opacity-80">{t.description}</div>
										<div className="text-sm mt-1">Priorité: {t.priority}</div>
										<div className="mt-2 flex gap-2">
											<button className="text-sm underline" onClick={() => updateTaskStatus(t.id, 'in_progress')}>En cours</button>
											<button className="text-sm underline" onClick={() => updateTaskStatus(t.id, 'done')}>Terminer</button>
											<button className="text-sm underline" onClick={() => startEdit(t)}>Éditer</button>
											<button className="text-sm underline text-red-600" onClick={() => deleteTask(t.id)}>Supprimer</button>
										</div>
									</>
								)}
							</li>
						))}
					</ul>
					</div>
					<div onDragOver={onDragOver} onDrop={(e) => onDrop(e, 'in_progress')}>
					<h4 className="font-semibold mb-2">En cours</h4>
					<ul className="space-y-2">
						{tasks.filter(t => t.status === 'in_progress').map(t => (
							<li key={t.id} className="border rounded p-3" draggable onDragStart={(e) => onDragStart(e, t.id)}>
								{editingId === t.id ? (
									<div className="space-y-2">
										<input className="border rounded px-2 py-1 text-black w-full" value={editTitle} onChange={e => setEditTitle(e.target.value)} />
										<textarea className="border rounded px-2 py-1 text-black w.full" value={editDescription} onChange={e => setEditDescription(e.target.value)} />
										<div className="flex gap-2">
											<button className="text-sm underline" onClick={saveEdit}>Enregistrer</button>
											<button className="text-sm underline" onClick={cancelEdit}>Annuler</button>
										</div>
									</div>
								) : (
									<>
										<div className="font-semibold">{t.title}</div>
										<div className="text-sm opacity-80">{t.description}</div>
										<div className="text-sm mt-1">Priorité: {t.priority}</div>
										<div className="mt-2 flex gap-2">
											<button className="text-sm underline" onClick={() => updateTaskStatus(t.id, 'todo')}>À faire</button>
											<button className="text-sm underline" onClick={() => updateTaskStatus(t.id, 'done')}>Terminer</button>
											<button className="text-sm underline" onClick={() => startEdit(t)}>Éditer</button>
											<button className="text-sm underline text-red-600" onClick={() => deleteTask(t.id)}>Supprimer</button>
										</div>
									</>
								)}
							</li>
						))}
					</ul>
					</div>
					<div onDragOver={onDragOver} onDrop={(e) => onDrop(e, 'done')}>
					<h4 className="font-semibold mb-2">Terminées</h4>
					<ul className="space-y-2">
						{tasks.filter(t => t.status === 'done').map(t => (
							<li key={t.id} className="border rounded p-3" draggable onDragStart={(e) => onDragStart(e, t.id)}>
								{editingId === t.id ? (
									<div className="space-y-2">
										<input className="border rounded px-2 py-1 text-black w-full" value={editTitle} onChange={e => setEditTitle(e.target.value)} />
										<textarea className="border rounded px-2 py-1 text-black w.full" value={editDescription} onChange={e => setEditDescription(e.target.value)} />
										<div className="flex gap-2">
											<button className="text-sm underline" onClick={saveEdit}>Enregistrer</button>
											<button className="text-sm underline" onClick={cancelEdit}>Annuler</button>
										</div>
									</div>
								) : (
									<>
										<div className="font-semibold line-through opacity-70">{t.title}</div>
										<div className="mt-2 flex gap-2">
											<button className="text-sm underline" onClick={() => startEdit(t)}>Éditer</button>
											<button className="text-sm underline text-red-600" onClick={() => deleteTask(t.id)}>Supprimer</button>
										</div>
									</>
								)}
							</li>
						))}
					</ul>
					</div>
				</>
				)}
			</div>
			<ul className="space-y-2">
				{projects.map(p => (
					<li key={p.id} className="border rounded p-3">
						<div className="font-semibold">{p.title}</div>
						<div className="text-sm opacity-80">{p.description}</div>
					</li>
				))}
			</ul>
		</div>
	)
}

