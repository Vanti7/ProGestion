import os
import re
from flask import Blueprint, jsonify, request, abort

from .. import db
from ..models import Project, KanbanBoard, KanbanColumn

bp = Blueprint("projects", __name__)


@bp.get("/projects")
def list_projects():
	projects = Project.query.order_by(Project.created_at.desc()).all()
	return jsonify([
		{
			"id": p.id,
			"title": p.title,
			"description": p.description,
			"status": p.status,
			"progress_percent": p.progress_percent,
			"priority": p.priority,
			"owner_id": p.owner_id,
			"roadmap_path": p.roadmap_path,
		}
		for p in projects
	])


@bp.post("/projects")
def create_project():
	data = request.get_json() or {}
	if not data.get("title") or not data.get("owner_id"):
		abort(400, "title and owner_id are required")
	project = Project(
		title=data["title"],
		description=data.get("description"),
		status=data.get("status", "planned"),
		progress_percent=int(data.get("progress_percent", 0)),
		priority=data.get("priority", "medium"),
		owner_id=int(data["owner_id"]),
		roadmap_path=data.get("roadmap_path"),
	)
	db.session.add(project)
	db.session.commit()
	# Create default Kanban board with 3 columns
	board = KanbanBoard(project_id=project.id)
	db.session.add(board)
	db.session.flush()
	for idx, name in enumerate(["À faire", "En cours", "Terminées"]):
		col = KanbanColumn(board_id=board.id, name=name, order_index=idx)
		db.session.add(col)
	db.session.commit()
	return jsonify({"id": project.id}), 201


@bp.get("/projects/<int:project_id>")
def get_project(project_id: int):
	project = Project.query.get_or_404(project_id)
	return jsonify(
		{
			"id": project.id,
			"title": project.title,
			"description": project.description,
			"status": project.status,
			"progress_percent": project.progress_percent,
			"priority": project.priority,
			"owner_id": project.owner_id,
			"roadmap_path": project.roadmap_path,
		}
	)


@bp.put("/projects/<int:project_id>")
def update_project(project_id: int):
	project = Project.query.get_or_404(project_id)
	data = request.get_json() or {}
	for field in ["title", "description", "status", "priority"]:
		if field in data:
			setattr(project, field, data[field])
	if "progress_percent" in data:
		project.progress_percent = int(data["progress_percent"])  # type: ignore
	db.session.commit()
	return jsonify({"status": "updated"})


@bp.delete("/projects/<int:project_id>")
def delete_project(project_id: int):
	project = Project.query.get_or_404(project_id)
	db.session.delete(project)
	db.session.commit()
	return jsonify({"status": "deleted"})



def _find_roadmap_candidates(search_root: str):
	candidates = []
	name_patterns = [re.compile(r"roadmap.*\.md$", re.IGNORECASE)]
	for root, dirs, files in os.walk(search_root):
		depth = root[len(search_root):].count(os.sep)
		if depth > 4:
			dirs[:] = []
			continue
		for fn in files:
			lower = fn.lower()
			path = os.path.join(root, fn)
			if any(p.search(lower) for p in name_patterns):
				score = 0
				if lower == "roadmap.md":
					score += 10
				score -= depth
				try:
					with open(path, "r", encoding="utf-8", errors="ignore") as f:
						text = f.read(20000)
						if "- [ ]" in text or "- [x]" in text:
							score += 2
				except Exception:
					pass
				candidates.append((score, path))
	return [p for _, p in sorted(candidates, key=lambda t: t[0], reverse=True)[:10]]


@bp.get("/projects/<int:project_id>/detect-roadmap")
def detect_roadmap(project_id: int):
	# Optionally use a provided root, else default to repo root
	root = request.args.get("root") or os.getenv("ROADMAP_SEARCH_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
	paths = _find_roadmap_candidates(root)
	return jsonify({"candidates": paths})
