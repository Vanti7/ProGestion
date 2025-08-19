# Project Portfolio — Gestion de projet & Portfolio (K3s-ready)

Application full-stack moderne combinant gestion de projets (CRUD, Kanban, tâches) et portfolio public (bio, compétences, projets sélectionnés, dépôts GitHub). Sécurité renforcée (CORS, headers, rate limit), auth email+password + OAuth (GitHub/GitLab), intégration IA (génération/reformat de roadmap), déploiement Docker/K3s.

## Stack
- Frontend: React + TypeScript + Vite + Tailwind + shadcn/ui, React Router
- Backend: Flask, SQLAlchemy, Flask-JWT-Extended, Authlib (OAuth), Talisman, Limiter, CORS, OpenAI SDK
- DB: PostgreSQL (prod), SQLite (local)
- Conteneurs: Docker, docker-compose; Orchestration: K3s (Traefik Ingress)

## Démarrage rapide (local)
1. Copier `.env.example` en `.env` et renseigner les secrets (JWT, OAuth, OpenAI...)
2. Lancer via docker-compose:
```bash
cd docker
docker-compose up -d --build
```
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000/api

## Déploiement K3s (extrait)
- Manifests dans `k8s/` (Deployments, StatefulSet Postgres, Ingress Traefik, Secrets, NetworkPolicies).
- Configurer les secrets (`backend-secret.yaml`, `openai-secret.yaml`) et l’Ingress (`ingress.yaml`).
- Optionnel: cert-manager + Let’s Encrypt pour TLS en prod.

## Authentification
- Email/mot de passe (JWT)
- OAuth GitHub/GitLab (via Authlib), tokens stockés côté backend (prévoir chiffrement au repos)

## IA: Roadmap
- Template: `docs/ROADMAP_TEMPLATE.md`
- Endpoints:
  - `GET /api/ai/template`: récupère le template
  - `POST /api/ai/generate-roadmap` `{ mode: 'skeleton'|'reformat', idea?, raw? }`
- Page `Idéation`: génère ou reformate votre roadmap et peut créer directement les tâches dans un projet.

## Roadmap & Kanban
- Chaque projet possède un board Kanban (colonnes dynamiques, DnD tâches/colonnes).
- Import Markdown: `POST /api/tasks/import-roadmap` (par projet)
- Sync “intelligent”: `POST /api/tasks/smart-sync?project_id=...` (lit le fichier, reformate via IA si nécessaire)
- `roadmap_path` configurable par projet (dashboard > champ “Chemin du fichier roadmap”).

## Intégration GitHub
- OAuth + liste des dépôts
- Sélection de dépôts publiés côté portfolio

## Versionning sémantique
- Fichier version: `VERSION`
- Changelog: `CHANGELOG.md`
- Historique versions: `docs/VERSION_HISTORY.md`
- Script release: `scripts/release.sh`
  - Bump: `./scripts/release.sh patch|minor|major` ou `./scripts/release.sh 1.2.3`
  - Actions: vérification branche `dev`, MAJ `VERSION`, section `CHANGELOG.md`, append `VERSION_HISTORY.md`, commit `chore(release): vX.Y.Z`, tag annoté `vX.Y.Z`, `git push origin dev && git push origin vX.Y.Z`
  - Prérequis: dépôt git initialisé, remote `origin`, utilisateur git configuré (`user.name`, `user.email`), droits push.

## Variables d’environnement (exemples)
- `DATABASE_URL`, `JWT_SECRET_KEY`, `SECRET_KEY`, `ALLOWED_ORIGINS`
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITLAB_CLIENT_ID`, `GITLAB_CLIENT_SECRET`
- `OPENAI_API_KEY`, `OPENAI_MODEL`
- `ROADMAP_PATH` (fallback global), `TEMPLATE_PATH` (template IA)

## Sécurité
- CORS par liste d’origines
- Headers sécurité (Talisman)
- Rate limiting (Limiter)
- Secrets via `.env` local / `Secret` Kubernetes

## Scripts utiles
- Release: voir section “Versionning sémantique”

## Licence
MIT.
