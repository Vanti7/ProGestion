# Roadmap

## Déjà livré
- [x] Auth email/password + JWT, OAuth GitHub/GitLab (liaison comptes)
- [x] CRUD projets; CRUD tâches (basique) avec due date à la création
- [x] Kanban: board auto par projet, colonnes dynamiques; DnD colonnes + persistance de l’ordre; DnD tâches entre colonnes (kanban_column_id)
- [x] Synchronisation `roadmap.md` → tâches (parser checkbox/priorité/due/tag)
- [x] Portfolio public (`/user/:username`), endpoints settings; sélection projets publiés
- [x] GitHub: lister repos via OAuth; sélectionner et publier au portfolio; affichage sur la page publique
- [x] IA: génération de roadmap (endpoint OpenAI + page Idéation)
- [x] Sécurité: CORS restrictif (ALLOWED_ORIGINS), en-têtes (Talisman), rate limiting (Limiter)
- [x] Infra: Dockerfiles backend/frontend, docker-compose, manifests K3s (backend, frontend, Postgres), Ingress basique, NetworkPolicy DB

## Phase 1 — Noyau fonctionnel (P1, 1-2 semaines)
- [ ] [P1] Finaliser CRUD tâches (édition complète: titre, desc, priorité, due) due: 2025-08-25 #backend #tasks
- [ ] [P1] DnD tâches avec position persistée par colonne (ajouter champ position) due: 2025-08-27 #backend #kanban #frontend
- [ ] [P1] API Kanban: endpoint pour réordonner tâches dans colonne due: 2025-08-27 #backend #kanban
- [ ] [P1] UI Kanban: rendu colonnes dynamiques + DnD tâches/colonnes stable (tri par position) due: 2025-08-28 #frontend #kanban
- [ ] [P1] Page Dashboard: filtres (par priorité, due <-> retard) due: 2025-08-29 #frontend #ux
- [ ] [P1] Portfolio settings UI (headline, location, skills, website) due: 2025-08-29 #frontend #portfolio

## Phase 2 — Sécurité & Auth (P1, 1 semaine)
- [ ] [P1] Chiffrement au repos des tokens OAuth (Fernet + TOKENS_ENC_KEY) due: 2025-09-02 #security #oauth #backend
- [ ] [P1] Refresh tokens/rotation pour JWT (serveur-side blacklist ou courte durée + refresh) due: 2025-09-03 #security #auth #backend
- [ ] [P1] Renforcer CORS par env (origines multiples), headers sécurité Nginx frontend due: 2025-09-04 #security #devops
- [ ] [P2] MFA optionnel (TOTP) pour comptes email/password due: 2025-09-06 #security #auth

## Phase 3 — Intégrations VCS (P1/P2, 1-2 semaines)
- [ ] [P1] GitHub: stats de base (langage dominant, étoiles, commits 30j) due: 2025-09-09 #integrations #github #backend
- [ ] [P1] UI portfolio: cartes dépôts (langage, stars, lien) due: 2025-09-10 #frontend #portfolio
- [ ] [P2] GitLab: OAuth + liste repos + publication au portfolio due: 2025-09-12 #integrations #gitlab #backend #frontend
- [ ] [P2] Lier projet interne ↔ repo externe (affichage sur Dashboard/portfolio) due: 2025-09-13 #integrations #portfolio

## Phase 4 — IA & Roadmap (P2, 3-4 jours)
- [ ] [P2] Page Idéation: “Générer → prévisualiser → créer tâches du projet” (import direct sans fichier) due: 2025-09-16 #ai #frontend #backend
- [ ] [P2] Prompt engineering (garde-fous format, limites longueur) due: 2025-09-16 #ai
- [ ] [P3] Historique d’idéation par user due: 2025-09-17 #ai #backend

## Phase 5 — DevOps & Prod (P1/P2, 1-2 semaines)
- [ ] [P1] Cert-manager + Let’s Encrypt (Ingress TLS prod) due: 2025-09-20 #devops #k8s
- [ ] [P1] CI/CD: build/push images, déploiement K3s (GitHub Actions) due: 2025-09-21 #devops #ci
- [ ] [P1] Migrations Alembic activées (PG) + scripts init prod due: 2025-09-21 #backend #db
- [ ] [P2] NetworkPolicies front->back, back->db strictes due: 2025-09-22 #devops #k8s
- [ ] [P2] Observabilité: logs structurés + métriques (Prometheus) due: 2025-09-24 #devops #observability

## Phase 6 — Qualité & UX (P2/P3, continu)
- [ ] [P2] Tests backend (unit/integration) + seeds de démo due: 2025-09-26 #quality #tests
- [ ] [P2] Tests frontend (vitest/playwright) pages clefs due: 2025-09-27 #quality #tests
- [ ] [P2] Dark mode complet (portfolio & dashboard) due: 2025-09-27 #frontend #ux
- [ ] [P3] Accessibilité de base (contrastes, aria) due: 2025-09-28 #frontend #a11y
- [ ] [P2] Documentation: README + guides K3s + variables env + sécurité due: 2025-09-28 #docs

## Phase 7 — Nice to have (P3)
- [ ] [P3] Webhooks GitHub/GitLab pour rafraîchir stats/repos publiés due: 2025-10-02 #integrations
- [ ] [P3] Export/Import roadmap au format YAML/JSON due: 2025-10-03 #ai #roadmap
- [ ] [P3] Multi-tenancy (préparation) due: 2025-10-05 #architecture

## Tâches transverses (maintenance)
- [ ] [P2] Nettoyage linter/formatters, hooks pre-commit due: 2025-09-06 #quality
- [ ] [P2] Gestion erreurs API uniforme (schéma JSON) due: 2025-09-06 #backend
- [ ] [P2] Pages d’erreur frontend (401/403/404) due: 2025-09-07 #frontend

