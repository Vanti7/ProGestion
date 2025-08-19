from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .. import db
from ..models import KanbanBoard, KanbanColumn, Project

bp = Blueprint("kanban", __name__)


@bp.get("/kanban/board")
@jwt_required()
def get_board():
	project_id = request.args.get("project_id", type=int)
	if not project_id:
		return jsonify({"error": "project_id is required"}), 400
	board = KanbanBoard.query.filter_by(project_id=project_id).first()
	if not board:
		return jsonify({"columns": []})
	return jsonify({
		"board_id": board.id,
		"columns": [
			{"id": c.id, "name": c.name, "order_index": c.order_index, "wip_limit": c.wip_limit}
			for c in board.columns
		]
	})


@bp.post("/kanban/columns")
@jwt_required()
def add_column():
	data = request.get_json() or {}
	project_id = data.get("project_id")
	name = (data.get("name") or "").strip()
	if not project_id or not name:
		return jsonify({"error": "project_id and name required"}), 400
	board = KanbanBoard.query.filter_by(project_id=int(project_id)).first()
	if not board:
		board = KanbanBoard(project_id=int(project_id))
		db.session.add(board)
		db.session.flush()
	order_index = len(board.columns or [])
	col = KanbanColumn(board_id=board.id, name=name, order_index=order_index)
	db.session.add(col)
	db.session.commit()
	return jsonify({"id": col.id})


@bp.put("/kanban/columns/<int:column_id>")
@jwt_required()
def update_column(column_id: int):
	col = KanbanColumn.query.get_or_404(column_id)
	data = request.get_json() or {}
	if "name" in data:
		col.name = str(data["name"]) or col.name
	if "order_index" in data:
		col.order_index = int(data["order_index"])
	if "wip_limit" in data:
		col.wip_limit = int(data["wip_limit"]) if data["wip_limit"] is not None else None
	db.session.commit()
	return jsonify({"status": "updated"})


@bp.delete("/kanban/columns/<int:column_id>")
@jwt_required()
def delete_column(column_id: int):
	col = KanbanColumn.query.get_or_404(column_id)
	db.session.delete(col)
	db.session.commit()
	return jsonify({"status": "deleted"})

