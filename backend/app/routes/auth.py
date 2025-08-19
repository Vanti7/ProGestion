import os
import secrets
from datetime import timedelta

from flask import Blueprint, jsonify, request, redirect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth

from .. import db, limiter
from ..models import User, OAuthAccount

bp = Blueprint("auth", __name__)
oauth = OAuth()


def init_oauth(app):
	oauth.init_app(app)
	oauth.register(
		"github",
		client_id=os.getenv("GITHUB_CLIENT_ID", ""),
		client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
		access_token_url="https://github.com/login/oauth/access_token",
		authorize_url="https://github.com/login/oauth/authorize",
		api_base_url="https://api.github.com/",
		client_kwargs={"scope": "read:user user:email"},
	)
	oauth.register(
		"gitlab",
		client_id=os.getenv("GITLAB_CLIENT_ID", ""),
		client_secret=os.getenv("GITLAB_CLIENT_SECRET", ""),
		access_token_url="https://gitlab.com/oauth/token",
		authorize_url="https://gitlab.com/oauth/authorize",
		api_base_url="https://gitlab.com/api/v4/",
		client_kwargs={"scope": "read_user read_api"},
	)


@bp.post("/auth/register")
@limiter.limit("3/minute")
def register():
	data = request.get_json() or {}
	email = (data.get("email") or "").strip().lower()
	password = data.get("password") or ""
	username = (data.get("username") or "").strip() or None
	if not email or not password:
		return jsonify({"error": "email and password required"}), 400
	if User.query.filter_by(email=email).first():
		return jsonify({"error": "email already used"}), 400
	password_hash = generate_password_hash(password)
	user = User(email=email, password_hash=password_hash, username=username)
	db.session.add(user)
	db.session.commit()
	return jsonify({"status": "registered", "user_id": user.id}), 201


@bp.post("/auth/login")
@limiter.limit("5/minute")
def login():
	data = request.get_json() or {}
	email = (data.get("email") or "").strip().lower()
	password = data.get("password") or ""
	user = User.query.filter_by(email=email).first()
	if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
		return jsonify({"error": "invalid credentials"}), 401
	access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=12))
	return jsonify({"access_token": access_token, "token_type": "Bearer"})


@bp.get("/auth/me")
@jwt_required()
def me():
	user_id = int(get_jwt_identity())
	user = User.query.get_or_404(user_id)
	return jsonify({
		"id": user.id,
		"email": user.email,
		"username": user.username,
		"name": user.name,
		"bio": user.bio,
		"avatar_url": user.avatar_url,
	})


@bp.get("/auth/oauth/<provider>")
@limiter.limit("10/minute")
def oauth_authorize(provider: str):
	redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:5173/oauth/callback")
	client = oauth.create_client(provider)
	if client is None:
		return jsonify({"error": "provider not configured"}), 400
	# Encode le provider dans le redirect_uri pour le récupérer au callback
	sep = "&" if "?" in redirect_uri else "?"
	return client.authorize_redirect(f"{redirect_uri}{sep}provider={provider}")


@bp.get("/auth/oauth/callback")
@limiter.limit("30/minute")
def oauth_callback():
	provider = request.args.get("provider") or "github"
	client = oauth.create_client(provider)
	if client is None:
		return jsonify({"error": "provider not configured"}), 400
	token = client.authorize_access_token()
	user_info = None
	if provider == "github":
		user_info = client.get("user").json()
		provider_user_id = str(user_info.get("id"))
		email = (user_info.get("email") or "").lower() or f"{provider_user_id}@users.noreply.github.com"
		username = user_info.get("login")
		avatar_url = user_info.get("avatar_url")
	elif provider == "gitlab":
		user_info = client.get("user").json()
		provider_user_id = str(user_info.get("id"))
		email = (user_info.get("email") or "").lower()
		username = user_info.get("username")
		avatar_url = user_info.get("avatar_url") or user_info.get("avatar_url", None)
	else:
		return jsonify({"error": "unsupported provider"}), 400

	oauth_row = OAuthAccount.query.filter_by(provider=provider, provider_user_id=provider_user_id).first()
	if oauth_row:
		user = User.query.get(oauth_row.user_id)
	else:
		user = User.query.filter_by(email=email).first()
		if not user:
			# Create lightweight user
			user = User(email=email, username=username, avatar_url=avatar_url, name=username)
			db.session.add(user)
			db.session.commit()
		oauth_row = OAuthAccount(
			user_id=user.id,
			provider=provider,
			provider_user_id=provider_user_id,
			access_token=token.get("access_token"),
			refresh_token=token.get("refresh_token"),
			token_type=token.get("token_type"),
			expires_at=token.get("expires_at"),
		)
		db.session.add(oauth_row)
		db.session.commit()

	access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=12))
	# Frontend pourra récupérer le token via un fragment/hash ou param
	redirect_url = (os.getenv("OAUTH_REDIRECT_URI", "http://localhost:5173/oauth/callback")).rstrip("/")
	return redirect(f"{redirect_url}?token={access_token}&provider={provider}")

