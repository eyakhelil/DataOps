# Personne A : amont (ingestion et infrastructure)

Dossiers : `ingestion/`, `orchestration/`, `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.env.example`, `.gitignore`, `requirements.txt`, `data/`.
Le code est celui du dépôt `ecom-dataops` d'origine, non modifié.

## À faire cette semaine
- [ ] Créer le dépôt GitHub, y mettre le contenu de `repo/`, protéger `main` (voir `docs/WORKFLOW.md`).
- [ ] Avec B : remplir `docs/IDEE.md`, `docs/ARCHITECTURE.md`, `docs/INTERFACE.md`.
- [ ] Adapter `ingestion/ingest.py` à votre sujet : votre API, votre 2e source, une clé unique par table, `ingested_at`, upsert (pas de doublons).
- [ ] Vérifier `docker compose up` sur un clone neuf (voir « Points à vérifier » ci-dessous).
- [ ] Brancher une vraie alerte (webhook Discord/Slack dans `.env`, jamais dans Git).
- [ ] Remplir le `README.md` (vide dans le dépôt d'origine).
- [ ] Mettre à jour `docs/INTERFACE.md` à chaque changement de table brute (prévenir B).
- [ ] Plus tard : MinIO/S3, déploiement AWS, alerte de budget AWS dès le jour 1.

## Points à vérifier (constatés en lisant le code d'origine, non modifiés)
- `docker compose up` ne démarre que le **dashboard** ; le pipeline est dans le profil `pipeline` (`docker compose --profile pipeline up pipeline`). Le sujet demande que toute la plateforme démarre avec `docker compose up`.
- `orchestration/flow.py` appelle `dbt.exe` : cela fonctionne sous Windows, pas dans le conteneur Linux.
- Chemin DuckDB : dbt s'exécute dans `dbt_project/`, l'ingestion à la racine. Un `DUCKDB_PATH` relatif (`data/warehouse.duckdb`) ne pointe pas vers le même fichier pour les deux. Un chemin absolu règle le problème.
- Le dashboard ouvre DuckDB en lecture seule pendant que le pipeline écrit : DuckDB n'accepte qu'un écrivain à la fois.

## Livrable de la semaine
Les données brutes arrivent dans `raw.*` sans doublons : relancer l'ingestion deux fois donne le même nombre de lignes.

## À savoir expliquer à l'oral
Pourquoi `INSERT OR REPLACE` évite les doublons · ce que font les retries et le cron de Prefect · ce que contient `docker-compose.yml` · où sont les secrets. Et la partie de B.
