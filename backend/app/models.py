from __future__ import annotations

from datetime import datetime

from . import db


class TimestampMixin:
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(
		db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
	)


class User(db.Model, TimestampMixin):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False, index=True)
	password_hash = db.Column(db.String(255), nullable=True)
	username = db.Column(db.String(80), unique=True, nullable=True)
	name = db.Column(db.String(120), nullable=True)
	bio = db.Column(db.Text, nullable=True)
	avatar_url = db.Column(db.String(512), nullable=True)

	projects = db.relationship("Project", back_populates="owner", cascade="all,delete")


class Project(db.Model, TimestampMixin):
	__tablename__ = "projects"

	id = db.Column(db.Integer, primary_key=True)
	owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	title = db.Column(db.String(200), nullable=False)
	description = db.Column(db.Text, nullable=True)
	status = db.Column(db.String(50), default="planned", nullable=False)
	progress_percent = db.Column(db.Integer, default=0, nullable=False)
	priority = db.Column(db.String(20), default="medium", nullable=False)
	roadmap_path = db.Column(db.String(512), nullable=True)

	owner = db.relationship("User", back_populates="projects")
	tasks = db.relationship("Task", back_populates="project", cascade="all,delete")
	repository_links = db.relationship(
		"RepositoryLink", back_populates="project", cascade="all,delete"
	)
	kanban_board = db.relationship("KanbanBoard", back_populates="project", uselist=False, cascade="all,delete")


class Task(db.Model, TimestampMixin):
	__tablename__ = "tasks"

	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
	title = db.Column(db.String(200), nullable=False)
	description = db.Column(db.Text, nullable=True)
	status = db.Column(db.String(50), default="todo", nullable=False)
	priority = db.Column(db.String(20), default="medium", nullable=False)
	due_date = db.Column(db.DateTime, nullable=True)
	kanban_column_id = db.Column(db.Integer, db.ForeignKey("kanban_columns.id"), nullable=True, index=True)

	project = db.relationship("Project", back_populates="tasks")


class RepositoryLink(db.Model, TimestampMixin):
	__tablename__ = "repository_links"

	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
	provider = db.Column(db.String(20), nullable=False)  # github | gitlab
	repo_full_name = db.Column(db.String(255), nullable=False)
	last_synced_at = db.Column(db.DateTime, nullable=True)

	project = db.relationship("Project", back_populates="repository_links")


class OAuthAccount(db.Model, TimestampMixin):
	__tablename__ = "oauth_accounts"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
	provider = db.Column(db.String(50), nullable=False)  # github | gitlab
	provider_user_id = db.Column(db.String(255), nullable=False)
	access_token = db.Column(db.Text, nullable=True)
	refresh_token = db.Column(db.Text, nullable=True)
	token_type = db.Column(db.String(50), nullable=True)
	expires_at = db.Column(db.Integer, nullable=True)

	__table_args__ = (
		db.UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
	)

	user = db.relationship("User", backref=db.backref("oauth_accounts", cascade="all,delete"))


class PortfolioSettings(db.Model, TimestampMixin):
	__tablename__ = "portfolio_settings"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
	headline = db.Column(db.String(200), nullable=True)
	location = db.Column(db.String(120), nullable=True)
	skills = db.Column(db.Text, nullable=True)  # liste séparée par des virgules
	website_url = db.Column(db.String(255), nullable=True)

	user = db.relationship("User", backref=db.backref("portfolio_settings", uselist=False, cascade="all,delete"))


class PublicProject(db.Model, TimestampMixin):
	__tablename__ = "public_projects"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
	project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)

	__table_args__ = (
		db.UniqueConstraint("user_id", "project_id", name="uq_user_project_public"),
	)

	user = db.relationship("User")
	project = db.relationship("Project")


class PublicRepo(db.Model, TimestampMixin):
	__tablename__ = "public_repos"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
	provider = db.Column(db.String(20), nullable=False)  # github
	repo_full_name = db.Column(db.String(255), nullable=False)
	html_url = db.Column(db.String(512), nullable=True)
	description = db.Column(db.Text, nullable=True)
	language = db.Column(db.String(80), nullable=True)
	stars = db.Column(db.Integer, default=0, nullable=False)
	is_private = db.Column(db.Boolean, default=False, nullable=False)
	last_synced_at = db.Column(db.DateTime, nullable=True)

	__table_args__ = (
		db.UniqueConstraint("user_id", "provider", "repo_full_name", name="uq_user_provider_repo"),
	)


class KanbanBoard(db.Model, TimestampMixin):
	__tablename__ = "kanban_boards"

	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False, index=True)

	project = db.relationship("Project", back_populates="kanban_board")
	columns = db.relationship("KanbanColumn", back_populates="board", cascade="all,delete", order_by="KanbanColumn.order_index")


class KanbanColumn(db.Model, TimestampMixin):
	__tablename__ = "kanban_columns"

	id = db.Column(db.Integer, primary_key=True)
	board_id = db.Column(db.Integer, db.ForeignKey("kanban_boards.id"), nullable=False, index=True)
	name = db.Column(db.String(80), nullable=False)
	order_index = db.Column(db.Integer, default=0, nullable=False)
	wip_limit = db.Column(db.Integer, nullable=True)

	board = db.relationship("KanbanBoard", back_populates="columns")
	tasks = db.relationship("Task", backref="kanban_column")

