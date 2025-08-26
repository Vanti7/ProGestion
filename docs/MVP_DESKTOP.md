# MVP Desktop (PC) — ProGestion

Date: 2025-08-26
Version cible: 0.2.0

## Objectif
Fournir une application Desktop autonome (Windows en priorité) permettant de gérer ses projets et tâches en mode hors-ligne, sans dépendance serveur. Préparer la future synchronisation quand le serveur sera disponible.

## Portée fonctionnelle (MVP)
- Projets (local): créer, renommer, archiver, supprimer.
- Kanban par projet (local): colonnes dynamiques, CRUD tâches, réordonnancement simple.
- Tableau de bord local: liste des projets, compteur tâches par statut.
- Idéation locale: notes simples par projet (texte brut/markdown minimal).
- Import/Export JSON: sauvegarde/restauration de l’espace de travail local.
- Paramètres: base URL serveur (placeholder), thème, langue.

## Hors scope (pour MVP)
- Auth email/password et OAuth (serveur requis).
- IA roadmap et toute fonctionnalité nécessitant l’API backend.
- Portfolio public et publication en ligne.
- Synchronisation multi-appareils.

## Contraintes et choix techniques
- Shell Desktop: Electron (intégration rapide avec l’app React Vite existante).
- Stockage: IndexedDB via une librairie (p.ex. localforage) pour données structurées.
- Mode hors-ligne par défaut; la synchro sera une future itération.
- Accessibilité de base et mise en page responsive Desktop.

## Critères d’acceptation
- L’utilisateur peut gérer des projets et tâches sans connexion.
- Les données persistent localement entre redémarrages.
- Export JSON produit un fichier importable restituant l’état complet.
- L’app démarre dans un exécutable Windows et charge l’UI actuelle.

## Suivi et prochaine étape
- Implémenter le conteneur Electron + script démarrage/packaging.
- Introduire une couche `storage` locale (IndexedDB) isolée de l’UI.
- Ajouter import/export JSON et page Paramètres minimale.

