## Phase 1 — Enveloppe Desktop & Stockage local
- [ ] [P1] Ajouter Tauri au projet (init src-tauri) #desktop #build
- [ ] [P1] Scripts npm `desktop:dev` et `desktop:build` (mode desktop) #desktop #build
- [ ] [P1] Alias Vite `platform` → impl web/desktop sans if runtime #frontend #build
- [ ] [P1] Impl adapter `storage` web: IndexedDB (localforage) #frontend #storage
- [ ] [P1] Impl adapter `storage` desktop: fs IndexedDB/tauri-plugin-store #desktop #storage
- [ ] [P1] Page Paramètres (thème, langue, base URL placeholder) #frontend #settings

## Phase 2 — MVP Fonctionnel Offline
- [ ] [P1] CRUD projets local (create/rename/archive/delete) #frontend #storage
- [ ] [P1] Board Kanban local: colonnes dynamiques; CRUD tâches #frontend #kanban
- [ ] [P1] DnD tâches/colonnes (ordre persisté) #frontend #kanban
- [ ] [P1] Idéation locale: notes markdown simples par projet #frontend #ideation
- [ ] [P1] Tableau de bord local: compteurs par statut #frontend #dashboard

## Phase 3 — Import / Export
- [ ] [P1] Export JSON de l’espace de travail (fichier) #desktop #fs
- [ ] [P1] Import JSON avec validation de schéma #frontend #fs
- [ ] [P2] Déduplication/merge lors d’import (optionnel) #frontend #fs

## Phase 4 — Packaging & Distribution
- [ ] [P1] Icône app Windows + metadata (tauri.conf.json) #desktop #build
- [ ] [P1] Build MSI/EXE signé en local (auto-update désactivé) #desktop #release
- [ ] [P2] Guide d’installation dans README (pré-requis, rustup) #docs

## Phase 5 — Qualité
- [ ] [P2] Tests unitaires adapter `storage` (web/desktop) #quality #tests
- [ ] [P2] Tests e2e tâches/kanban (Playwright desktop) #quality #tests
- [ ] [P2] Télémetrie désactivée par défaut, opt-in #privacy #quality

## Phase 6 — Pré-synchro (future itération)
- [ ] [P2] Définir schéma de sync (UUIDs, timestamps, versions) #sync #architecture
- [ ] [P2] Placer points d’extension `syncService` (no-op offline) #sync

