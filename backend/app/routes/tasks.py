import os
import re
from datetime import datetime

from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import db
from ..models import Task, KanbanColumn, Project
from textwrap import dedent

bp = Blueprint("tasks", __name__)


@bp.get("/tasks")
@jwt_required()
def list_tasks():
	project_id = request.args.get("project_id", type=int)
	query = Task.query
	if project_id is not None:
		query = query.filter(Task.project_id == project_id)
	column_id = request.args.get("column_id", type=int)
	if column_id is not None:
		query = query.filter(Task.kanban_column_id == column_id)
	tasks = query.order_by(Task.created_at.desc()).all()
	return jsonify([
		{
			"id": t.id,
			"title": t.title,
			"description": t.description,
			"status": t.status,
			"priority": t.priority,
			"due_date": t.due_date.isoformat() if t.due_date else None,
			"project_id": t.project_id,
			"kanban_column_id": t.kanban_column_id,
		}
		for t in tasks
	])


@bp.post("/tasks")
@jwt_required()
def create_task():
	data = request.get_json() or {}
	if not data.get("title") or not data.get("project_id"):
		abort(400, "title and project_id are required")
	task = Task(
		title=data["title"],
		description=data.get("description"),
		status=data.get("status", "todo"),
		priority=data.get("priority", "medium"),
		project_id=int(data["project_id"]),
	)
	if data.get("due_date"):
		try:
			task.due_date = datetime.fromisoformat(str(data["due_date"]))
		except Exception:
			pass
	# Column from body
	if data.get("kanban_column_id"):
		try:
			col = KanbanColumn.query.get(int(data["kanban_column_id"]))
			if col:
				task.kanban_column_id = col.id
		except Exception:
			pass
	# Default to column from query param if provided
	default_column_id = request.args.get("column_id", type=int)
	if default_column_id:
		col = KanbanColumn.query.get(default_column_id)
		if col:
			task.kanban_column_id = default_column_id
	db.session.add(task)
	db.session.commit()
	return jsonify({"id": task.id}), 201


@bp.put("/tasks/<int:task_id>")
@jwt_required()
def update_task(task_id: int):
	task = Task.query.get_or_404(task_id)
	data = request.get_json() or {}
	for field in ["title", "description", "status", "priority"]:
		if field in data:
			setattr(task, field, data[field])
	# Move to another column
	if "kanban_column_id" in data:
		col = KanbanColumn.query.get(int(data["kanban_column_id"]))
		if col:
			task.kanban_column_id = col.id
	db.session.commit()
	return jsonify({"status": "updated"})


@bp.delete("/tasks/<int:task_id>")
@jwt_required()
def delete_task(task_id: int):
	task = Task.query.get_or_404(task_id)
	db.session.delete(task)
	db.session.commit()
	return jsonify({"status": "deleted"})


def parse_roadmap_markdown(markdown_text: str):
	# Patterns: "- [ ] task title", "- [x] done task"
	# Optional tags: #tag, priority [P1|P2|P3], due: YYYY-MM-DD
	items = []
	checkbox_re = re.compile(r"^- \[( |x)\] (.+)$")
	priority_re = re.compile(r"\[(P[1-3])\]")
	due_re = re.compile(r"due:\s*(\d{4}-\d{2}-\d{2})")
	tag_re = re.compile(r"#(\w+)")
	for line in markdown_text.splitlines():
		m = checkbox_re.match(line.strip())
		if not m:
			continue
		checked, title = m.groups()
		status = "done" if checked == "x" else "todo"
		priority_match = priority_re.search(title)
		priority = "medium"
		if priority_match:
			p = priority_match.group(1)
			priority = {"P1": "high", "P2": "medium", "P3": "low"}.get(p, "medium")
		due_match = due_re.search(title)
		due_date = None
		if due_match:
			try:
				due_date = datetime.fromisoformat(due_match.group(1))
			except Exception:
				pass
		tags = tag_re.findall(title)
		clean_title = re.sub(priority_re, "", title)
		clean_title = re.sub(due_re, "", clean_title)
		clean_title = re.sub(tag_re, "", clean_title).strip()
		items.append({
			"title": clean_title.strip("- "),
			"status": status,
			"priority": priority,
			"due_date": due_date.isoformat() if due_date else None,
			"tags": tags,
		})
	return items


@bp.post("/tasks/sync-roadmap")
@jwt_required()
def sync_roadmap():
	project_id = request.args.get("project_id", type=int)
	if not project_id:
		return jsonify({"error": "project_id is required"}), 400
	# Use project-specific path if provided
	roadmap_path = None
	project = Project.query.get(project_id)
	if project and project.roadmap_path:
		roadmap_path = project.roadmap_path
	else:
		roadmap_path = os.getenv("ROADMAP_PATH", os.path.join(os.path.dirname(__file__), "../../..", "roadmap.md"))
	try:
		with open(roadmap_path, "r", encoding="utf-8") as f:
			content = f.read()
	except FileNotFoundError:
		return jsonify({"error": f"roadmap not found at {roadmap_path}"}), 404

	items = parse_roadmap_markdown(content)
	created_ids = []
	for item in items:
		# Avoid naive duplicates by title within this project
		exists = Task.query.filter(Task.project_id == project_id, Task.title == item["title"]).first()
		if exists:
			continue
		task = Task(
			project_id=project_id,
			title=item["title"],
			description=None,
			status=item["status"],
			priority=item["priority"],
		)
		if item.get("due_date"):
			try:
				task.due_date = datetime.fromisoformat(item["due_date"])  # type: ignore
			except Exception:
				pass
		db.session.add(task)
		db.session.commit()
		created_ids.append(task.id)

	return jsonify({"created": created_ids, "total": len(items)})


@bp.post("/tasks/import-roadmap")
@jwt_required()
def import_roadmap():
	data = request.get_json() or {}
	project_id = int(data.get("project_id") or 0)
	markdown = (data.get("markdown") or "").strip()
	if not project_id or not markdown:
		return jsonify({"error": "project_id and markdown are required"}), 400

	items = parse_roadmap_markdown(markdown)
	created_ids = []
	for item in items:
		exists = Task.query.filter(Task.project_id == project_id, Task.title == item["title"]).first()
		if exists:
			continue
		task = Task(
			project_id=project_id,
			title=item["title"],
			description=None,
			status=item["status"],
			priority=item["priority"],
		)
		if item.get("due_date"):
			try:
				task.due_date = datetime.fromisoformat(item["due_date"])  # type: ignore
			except Exception:
				pass
		db.session.add(task)
		db.session.commit()
		created_ids.append(task.id)

	return jsonify({"created": created_ids, "total": len(items)})


@bp.post("/tasks/smart-sync")
@jwt_required()
def smart_sync():
	project_id = request.args.get("project_id", type=int)
	if not project_id:
		return jsonify({"error": "project_id is required"}), 400
	roadmap_path = None
	project = Project.query.get(project_id)
	if project and project.roadmap_path:
		roadmap_path = project.roadmap_path
	else:
		roadmap_path = os.getenv("ROADMAP_PATH", os.path.join(os.path.dirname(__file__), "../../..", "roadmap.md"))
	try:
		with open(roadmap_path, "r", encoding="utf-8") as f:
			content = f.read()
	except FileNotFoundError:
		# Essayer détection simple à la racine du repo si aucun chemin défini
		return jsonify({"error": f"roadmap not found at {roadmap_path}", "suggest": "use_ideation"}), 404

	items = parse_roadmap_markdown(content)
	if not items:
		# Tente reformatage via IA
		api_key = os.getenv("OPENAI_API_KEY")
		if api_key:
			# Charger le template
			template_path = os.getenv("TEMPLATE_PATH", os.path.join(os.path.dirname(__file__), "../../docs/ROADMAP_TEMPLATE.md"))
			try:
				with open(template_path, "r", encoding="utf-8") as tf:
					template = tf.read()
			except Exception:
				template = ""
			try:
				from openai import OpenAI
				client = OpenAI(api_key=api_key)
				prompt = dedent(f"""
				Tu es un assistant qui produit des roadmaps strictement formatées et exploitables par une application.
				Convertis le texte suivant au format EXACT du template, en supprimant tout texte hors listes et en corrigeant si nécessaire priorités/tags/dates.
				=== TEMPLATE ===
				{template}
				=== FIN TEMPLATE ===

				Texte à reformater:
				---
				{content}
				---

				Tâche: Retourne UNIQUEMENT la liste normalisée, sans aucune autre phrase.
				""")
				resp = client.chat.completions.create(
					model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
					messages=[
						{"role": "system", "content": "Tu es un assistant qui produit des roadmaps strictement formatées et exploitables par une application."},
						{"role": "user", "content": prompt},
					],
					temperature=0.2,
				)
				content_norm = resp.choices[0].message.content or ""
				items = parse_roadmap_markdown(content_norm)
			except Exception:
				# fallback best-effort: extraire lignes déjà valides
				lines = [ln for ln in content.splitlines() if ln.strip().startswith("- [")]
				content_norm = "\n".join(lines)
				items = parse_roadmap_markdown(content_norm)

	created_ids = []
	for item in items:
		exists = Task.query.filter(Task.project_id == project_id, Task.title == item["title"]).first()
		if exists:
			continue
		task = Task(
			project_id=project_id,
			title=item["title"],
			description=None,
			status=item["status"],
			priority=item["priority"],
		)
		if item.get("due_date"):
			try:
				task.due_date = datetime.fromisoformat(item["due_date"])  # type: ignore
			except Exception:
				pass
		db.session.add(task)
		db.session.commit()
		created_ids.append(task.id)

	return jsonify({"created": created_ids, "total": len(items)})

