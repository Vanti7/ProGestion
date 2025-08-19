# Modèle de Roadmap (format attendu par l’IA et le parseur)

Objectif: produire une roadmap exploitable automatiquement par l’application. Respecter strictement ce format.

## Règles générales
- Uniquement des listes de tâches Markdown (pas de paragraphes explicatifs hors listes).
- Chaque tâche est UNE ligne commençant par une case à cocher:
  - `- [ ] ...` pour à faire
  - `- [x] ...` pour terminée
- Priorité obligatoire entre crochets: `[P1]`, `[P2]` ou `[P3]`.
- Date d’échéance optionnelle: `due: YYYY-MM-DD`.
- Tags optionnels: `#tag` (un ou plusieurs).
- 10 à 20 tâches maximum par phase; phrases courtes et actionnables.

## Structure recommandée par phases
- Les phases sont de simples sous-titres (optionnels) pour la lisibilité humaine; le parseur ignore les titres.
- Exemple de titres: `## Phase 1 — Noyau`, `## Phase 2 — Sécurité`, etc.

## Exemples de lignes valides
- `- [ ] [P1] Mettre en place migrations Alembic due: 2025-09-01 #backend #db`
- `- [x] [P2] Créer la page d’accueil du portfolio #frontend #ui`
- `- [ ] [P3] Ajouter dark mode #frontend #ux`

## Exemple de roadmap complète

## Phase 1 — Noyau
- [ ] [P1] Implémenter CRUD projets #backend
- [ ] [P1] Implémenter CRUD tâches #backend #tasks
- [ ] [P1] Créer board Kanban avec 3 colonnes par défaut due: 2025-09-01 #kanban #backend
- [ ] [P2] Lier tâches à colonnes Kanban #kanban #backend

## Phase 2 — Portfolio
- [ ] [P1] Page publique `/user/:username` (bio, skills, projets publiés) #frontend #portfolio
- [ ] [P2] Sélectionner projets à publier dans Dashboard #frontend #portfolio
- [ ] [P2] Intégrer dépôts GitHub au portfolio #integrations #github #frontend

## Phase 3 — Sécurité & Devops
- [ ] [P1] CORS restrictif + en-têtes sécurité #security #backend
- [ ] [P1] Ingress K3s + TLS (cert-manager) due: 2025-09-10 #k8s #devops
- [ ] [P2] CI/CD build/push images #devops

## Contraintes de sortie de l’IA
- Ne pas produire d’explications, uniquement des lignes de tâches.
- Respecter la casse et l’ordre des éléments par ligne: `- [ ] [PX] Titre ... due: YYYY-MM-DD #tag1 #tag2`
- Limiter le nombre total de tâches à 40.
