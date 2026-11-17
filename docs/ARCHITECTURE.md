# Architecture visée

```mermaid
flowchart LR
    S1[Source 1 : API] --> ING[Ingestion Python / dlt]
    S2[Source 2 : fichier ou API] --> ING
    ING -->|upsert, sans doublons| RAW[(DuckDB : schéma raw)]
    RAW --> STG[dbt staging]
    STG --> INT[dbt intermediate]
    INT --> MART[dbt marts]
    MART --> DASH[Dashboard Streamlit]
    ORCH[Prefect : cron quotidien] -.déclenche.-> ING
    ORCH -.déclenche.-> STG
    CI[GitHub Actions] -.bloque une PR rouge.-> MART
    ORCH -.échec.-> ALERT[Alerte webhook]
```

Remplacer les noms par ceux de votre sujet, et ajouter votre idée « en plus » au schéma.

## Qui est responsable de quoi
| Couche | Dossier | Responsable |
|---|---|---|
| Ingestion, Docker, orchestration | `ingestion/`, `orchestration/`, `Dockerfile`, `docker-compose.yml` | A |
| dbt, tests, contrats, CI, dashboard | `dbt_project/`, `tests/`, `contracts/`, `.github/`, `dashboard/` | B |
