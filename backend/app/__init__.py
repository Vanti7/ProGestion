import os
from datetime import timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def create_app() -> Flask:
	app = Flask(__name__)

	app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
	app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
	app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

	# Database configuration
	database_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
	if database_url.startswith("postgres://"):
		# SQLAlchemy expects postgresql://
		database_url = database_url.replace("postgres://", "postgresql://", 1)
	app.config["SQLALCHEMY_DATABASE_URI"] = database_url
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

	# Initialize extensions
	db.init_app(app)
	migrate.init_app(app, db)
	jwt.init_app(app)
	# CORS restrictif via ALLOWED_ORIGINS (séparées par des virgules)
	allowed = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
	CORS(app, resources={r"/api/*": {"origins": allowed, "supports_credentials": False}})

	# Sécurité HTTP (CSP, HSTS, etc.)
	csp = {
		'default-src': ["'self'"],
		'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
		'style-src': ["'self'", "'unsafe-inline'"],
		'img-src': ["'self'", 'data:'],
		'connect-src': ["'self'", *allowed],
	}
	Talisman(
		app,
		content_security_policy=csp,
		force_https=False,
		frame_options='DENY',
		referrer_policy='no-referrer',
		session_cookie_secure=True,
		session_cookie_http_only=True,
	)

	# Rate limiting (anti brute-force)
	limiter.init_app(app)

	# Blueprints
	from .routes.health import bp as health_bp
	app.register_blueprint(health_bp, url_prefix="/api")
	from .routes.projects import bp as projects_bp
	app.register_blueprint(projects_bp, url_prefix="/api")
	from .routes.tasks import bp as tasks_bp
	app.register_blueprint(tasks_bp, url_prefix="/api")
	from .routes.auth import bp as auth_bp
	from .routes.auth import init_oauth
	app.register_blueprint(auth_bp, url_prefix="/api")
	init_oauth(app)
	from .routes.ai import bp as ai_bp
	app.register_blueprint(ai_bp, url_prefix="/api")
	from .routes.portfolio import bp as portfolio_bp
	app.register_blueprint(portfolio_bp, url_prefix="/api")
	from .routes.kanban import bp as kanban_bp
	app.register_blueprint(kanban_bp, url_prefix="/api")

	# Optional: auto create DB tables in dev to avoid running migrations
	if os.getenv("AUTO_CREATE_DB", "false").lower() == "true":
		with app.app_context():
			db.create_all()
			# Seed minimal data for demo
			try:
				from .models import User, Project  # type: ignore
				if not User.query.first():
					user = User(email="demo@example.com", username="demo", name="Demo User")
					db.session.add(user)
					db.session.commit()
					project = Project(
						owner_id=user.id,
						title="Projet de démonstration",
						description="Exemple de projet initial",
						status="in_progress",
						progress_percent=25,
						priority="medium",
					)
					db.session.add(project)
					db.session.commit()
			except Exception:
				# Ne bloque pas le démarrage en cas d'erreur de seed
				pass

	return app


# Import models for migration discovery
from . import models  # noqa: E402,F401

