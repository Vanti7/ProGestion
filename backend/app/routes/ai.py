import os
from textwrap import dedent

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .. import limiter

bp = Blueprint("ai", __name__)


SYSTEM_PROMPT_BASE = "Tu es un assistant qui produit des roadmaps strictement formatées et exploitables par une application."


def read_template() -> str:
	template_path = os.getenv("TEMPLATE_PATH", os.path.join(os.path.dirname(__file__), "../../docs/ROADMAP_TEMPLATE.md"))
	try:
		with open(template_path, "r", encoding="utf-8") as f:
			return f.read()
	except Exception:
		return ""


def build_prompt_skeleton(user_idea: str, template: str) -> str:
	return dedent(
		f"""
		{SYSTEM_PROMPT_BASE}
		Respecte STRICTEMENT le format décrit ci-dessous (pas d'autres textes):
		=== TEMPLATE ===
		{template}
		=== FIN TEMPLATE ===

		Idée utilisateur:
		{user_idea}

		Tâche: Générer une roadmap SQUELETTE conforme au template, 10-20 items max, sans explications.
		"""
	)


def build_prompt_reformat(raw_text: str, template: str) -> str:
	return dedent(
		f"""
		{SYSTEM_PROMPT_BASE}
		Convertis le texte suivant au format EXACT du template, en supprimant tout texte hors listes et en corrigeant si nécessaire priorités/tags/dates.
		=== TEMPLATE ===
		{template}
		=== FIN TEMPLATE ===

		Texte à reformater:
		---
		{raw_text}
		---

		Tâche: Retourne UNIQUEMENT la liste normalisée, sans aucune autre phrase.
		"""
	)


@bp.post("/ai/generate-roadmap")
@jwt_required()
@limiter.limit("10/minute")
def generate_roadmap():
	data = request.get_json() or {}
	mode = (data.get("mode") or "skeleton").strip()
	idea = (data.get("idea") or "").strip()
	raw_text = (data.get("raw") or "").strip()
	template = read_template()
	if mode == "skeleton" and not idea:
		return jsonify({"error": "idea is required for skeleton mode"}), 400
	if mode == "reformat" and not raw_text:
		return jsonify({"error": "raw is required for reformat mode"}), 400

	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		if mode == "skeleton":
			fallback = "\n".join([
				"- [ ] [P1] Définir le scope du projet due: 2025-09-01 #planning",
				"- [ ] [P1] Créer le backlog initial #tasks",
				"- [ ] [P2] Mettre en place CI/CD #devops",
				"- [ ] [P3] Rédiger README et documentation #docs",
			])
		else:
			lines = [ln for ln in raw_text.splitlines() if ln.strip().startswith("- [")]
			fallback = "\n".join(lines[:40])
		return jsonify({"roadmap": fallback, "provider": "fallback"})

	try:
		from openai import OpenAI
		client = OpenAI(api_key=api_key)
		if mode == "reformat":
			prompt = build_prompt_reformat(raw_text, template)
		else:
			prompt = build_prompt_skeleton(idea, template)
		resp = client.chat.completions.create(
			model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
			messages=[
				{"role": "system", "content": SYSTEM_PROMPT_BASE},
				{"role": "user", "content": prompt},
			],
			temperature=0.2,
		)
		content = resp.choices[0].message.content or ""
		return jsonify({"roadmap": content, "provider": "openai"})
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@bp.get("/ai/template")
@jwt_required()
@limiter.limit("30/minute")
def get_template():
	return jsonify({"template": read_template()})

