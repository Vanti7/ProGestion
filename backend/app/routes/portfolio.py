from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import db
from ..models import User, Project, PublicProject, PortfolioSettings, OAuthAccount, PublicRepo
import requests
from datetime import datetime

bp = Blueprint("portfolio", __name__)


@bp.get("/portfolio/<username>")
def public_portfolio(username: str):
	user = User.query.filter_by(username=username).first_or_404()
	settings = PortfolioSettings.query.filter_by(user_id=user.id).first()
	public_links = PublicProject.query.filter_by(user_id=user.id).all()
	project_ids = [pl.project_id for pl in public_links]
	projects = Project.query.filter(Project.id.in_(project_ids)).all() if project_ids else []
	repos = PublicRepo.query.filter_by(user_id=user.id, provider="github").all()
	return jsonify({
		"user": {
			"username": user.username,
			"name": user.name,
			"bio": user.bio,
			"avatar_url": user.avatar_url,
		},
		"settings": {
			"headline": settings.headline if settings else None,
			"location": settings.location if settings else None,
			"skills": settings.skills.split(",") if (settings and settings.skills) else [],
			"website_url": settings.website_url if settings else None,
		},
		"projects": [
			{"id": p.id, "title": p.title, "description": p.description, "status": p.status, "progress_percent": p.progress_percent}
			for p in projects
		],
		"repos": [
			{
				"provider": r.provider,
				"full_name": r.repo_full_name,
				"html_url": r.html_url,
				"description": r.description,
				"language": r.language,
				"stars": r.stars,
			}
			for r in repos
		]
	})


@bp.get("/portfolio/me")
@jwt_required()
def get_my_portfolio():
	user_id = int(get_jwt_identity())
	user = User.query.get_or_404(user_id)
	settings = PortfolioSettings.query.filter_by(user_id=user_id).first()
	links = PublicProject.query.filter_by(user_id=user_id).all()
	repos = PublicRepo.query.filter_by(user_id=user_id).all()
	return jsonify({
		"user": {"email": user.email, "username": user.username, "name": user.name, "bio": user.bio, "avatar_url": user.avatar_url},
		"settings": {
			"headline": settings.headline if settings else None,
			"location": settings.location if settings else None,
			"skills": settings.skills.split(",") if (settings and settings.skills) else [],
			"website_url": settings.website_url if settings else None,
		},
		"public_project_ids": [l.project_id for l in links],
		"public_repos": [
			{
				"provider": r.provider,
				"full_name": r.repo_full_name,
				"html_url": r.html_url,
				"description": r.description,
				"language": r.language,
				"stars": r.stars,
			}
			for r in repos
		]
	})


@bp.post("/portfolio/me")
@jwt_required()
def update_my_portfolio():
	user_id = int(get_jwt_identity())
	data = request.get_json() or {}
	settings = PortfolioSettings.query.filter_by(user_id=user_id).first()
	if not settings:
		settings = PortfolioSettings(user_id=user_id)
		db.session.add(settings)
	settings.headline = data.get("headline")
	settings.location = data.get("location")
	skills = data.get("skills")
	if isinstance(skills, list):
		settings.skills = ",".join([str(s).strip() for s in skills if str(s).strip()])
	settings.website_url = data.get("website_url")
	db.session.commit()
	return jsonify({"status": "updated"})


@bp.post("/portfolio/me/projects")
@jwt_required()
def set_public_projects():
	user_id = int(get_jwt_identity())
	data = request.get_json() or {}
	ids = data.get("project_ids") or []
	if not isinstance(ids, list):
		return jsonify({"error": "project_ids must be a list"}), 400
	# Clear existing
	PublicProject.query.filter_by(user_id=user_id).delete()
	# Insert new
	for pid in ids:
		try:
			pid_int = int(pid)
			# ensure ownership
			project = Project.query.get(pid_int)
			if project and project.owner_id == user_id:
				link = PublicProject(user_id=user_id, project_id=pid_int)
				db.session.add(link)
		except Exception:
			continue
	db.session.commit()
	return jsonify({"status": "updated", "count": len(ids)})


@bp.get("/portfolio/me/github/repos")
@jwt_required()
def list_my_github_repos():
	user_id = int(get_jwt_identity())
	acct = OAuthAccount.query.filter_by(user_id=user_id, provider="github").first()
	if not acct or not acct.access_token:
		return jsonify({"error": "github account not linked"}), 400
	headers = {"Authorization": f"token {acct.access_token}", "Accept": "application/vnd.github+json"}
	resp = requests.get("https://api.github.com/user/repos?per_page=100", headers=headers, timeout=15)
	if resp.status_code != 200:
		return jsonify({"error": "failed to fetch repos"}), 502
	repos = [
		{
			"full_name": r.get("full_name"),
			"html_url": r.get("html_url"),
			"description": r.get("description"),
			"language": r.get("language"),
			"stargazers_count": r.get("stargazers_count"),
			"private": r.get("private"),
		}
		for r in resp.json()
	]
	return jsonify(repos)


@bp.post("/portfolio/me/github/publish")
@jwt_required()
def set_public_github_repos():
	user_id = int(get_jwt_identity())
	data = request.get_json() or {}
	repos = data.get("repos") or []  # list of {full_name, html_url, description, language, stars, private}
	if not isinstance(repos, list):
		return jsonify({"error": "repos must be a list"}), 400
	# Clear existing github repos
	PublicRepo.query.filter_by(user_id=user_id, provider="github").delete()
	for r in repos:
		try:
			row = PublicRepo(
				user_id=user_id,
				provider="github",
				repo_full_name=str(r.get("full_name")),
				html_url=r.get("html_url"),
				description=r.get("description"),
				language=r.get("language"),
				stars=int(r.get("stargazers_count") or 0),
				is_private=bool(r.get("private")),
				last_synced_at=datetime.utcnow(),
			)
			db.session.add(row)
		except Exception:
			continue
	db.session.commit()
	return jsonify({"status": "updated", "count": len(repos)})

