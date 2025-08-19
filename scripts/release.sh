#!/usr/bin/env bash
set -euo pipefail

# Release script: bump version, update changelog/history, commit and optionally tag
# Usage:
#   ./scripts/release.sh patch|minor|major [--prepare]
#   ./scripts/release.sh 1.2.3 [--prepare]

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$REPO_ROOT"

current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

# Mode prepare: pas de tag, pas de push du tag, utile sur branches release/x.y.z
prepare_only=false
if [[ "${2:-}" == "--prepare" ]]; then
  prepare_only=true
fi

if [[ "$prepare_only" != true && "$current_branch" != "dev" ]]; then
  echo "Erreur: les releases non-préparées ne sont autorisées que depuis 'dev' (branche actuelle: $current_branch)" >&2
  exit 1
fi

if [[ ! -f VERSION ]]; then
  echo "0.0.0" > VERSION
fi

current_version=$(cat VERSION | tr -d '[:space:]')

function inc_semver() {
  local ver="$1" part="$2"
  IFS='.' read -r major minor patch <<<"$ver"
  major=${major:-0}; minor=${minor:-0}; patch=${patch:-0}
  case "$part" in
    major) major=$((major+1)); minor=0; patch=0;;
    minor) minor=$((minor+1)); patch=0;;
    patch) patch=$((patch+1));;
    *) echo "$part";;
  esac
  echo "${major}.${minor}.${patch}"
}

arg=${1:-}
if [[ -z "$arg" ]]; then
  echo "Usage: $0 patch|minor|major|X.Y.Z" >&2
  exit 1
fi

if [[ "$arg" =~ ^(patch|minor|major)$ ]]; then
  new_version=$(inc_semver "$current_version" "$arg")
elif [[ "$arg" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  new_version="$arg"
else
  echo "Argument invalide: $arg" >&2
  exit 1
fi

echo "$new_version" > VERSION

# Ensure files exist
[[ -f CHANGELOG.md ]] || echo -e "# Changelog\n" > CHANGELOG.md
[[ -f docs/VERSION_HISTORY.md ]] || { mkdir -p docs; echo -e "# Historique des versions\n" > docs/VERSION_HISTORY.md; }

# Update CHANGELOG: prepend a header for the version if not present
if ! grep -q "^## \[$new_version\]" CHANGELOG.md; then
  tmp=$(mktemp)
  {
    echo "# Changelog"
    echo
    echo "## [$new_version] - $(date +%Y-%m-%d)"
    echo "- Mise à jour version"
    echo
    # print rest without duplicate top title
    awk 'NR==1{if($0!="# Changelog"){print $0 nextfile}}1' CHANGELOG.md | sed '1d'
  } > "$tmp"
  mv "$tmp" CHANGELOG.md
fi

# Update VERSION_HISTORY
if ! grep -q "^\- $new_version" docs/VERSION_HISTORY.md; then
  echo "- $new_version — Release $(date +%Y-%m-%d)" >> docs/VERSION_HISTORY.md
fi

# Commit and push
git add VERSION CHANGELOG.md docs/VERSION_HISTORY.md
if [[ "$prepare_only" == true ]]; then
  git commit -m "chore(release): v$new_version (prepare)"
  git push origin "$current_branch"
  echo "Release v$new_version préparée sur $current_branch."
else
  git commit -m "chore(release): v$new_version"
  git tag -a "v$new_version" -m "Release v$new_version"
  git push origin dev
  git push origin "v$new_version"
  echo "Release v$new_version effectuée."
fi
