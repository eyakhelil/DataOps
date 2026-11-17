# Workflow Git (obligatoire pour la note)

1. `main` est protégée : rien n'y arrive sans pull request relue par l'autre.
2. Une branche par tâche : `feat/ingestion-api` (A), `feat/dbt-staging` (B), `fix/...`, `docs/...`.
3. Petits commits fréquents, messages clairs (`feat: ...`, `fix: ...`, `docs: ...`).
4. Chacun relit la PR de l'autre et laisse au moins un commentaire utile.
5. Chacun reste dans ses dossiers (voir `docs/ARCHITECTURE.md`). Un fichier partagé
   (`requirements.txt`, `docker-compose.yml`, `README.md`) se modifie par PR, en prévenant l'autre.

## Protéger `main` (une fois, par A, dans GitHub)
Settings -> Branches -> Add rule sur `main` : « Require a pull request before merging »,
« Require approvals : 1 », « Require status checks to pass » (après le premier run de la CI : choisir `checks`).

## Commandes utiles
```bash
git checkout -b feat/ma-tache
git add -A && git commit -m "feat: ..."
git push -u origin feat/ma-tache      # puis ouvrir la PR sur GitHub
git checkout main && git pull         # après le merge
```
