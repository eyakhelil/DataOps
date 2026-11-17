# Contrat d'interface entre A et B

A produit, B consomme. Tant que ce fichier est respecté, chacun avance sans attendre l'autre.
Toute modification se fait par une PR relue par l'autre.

## Base
`DUCKDB_PATH` (voir `.env.example`), schéma `raw`.

## Tables brutes (état actuel : exemple boutique, à remplacer par votre domaine)
| Table | Clé unique | Colonnes | Écrite par |
|---|---|---|---|
| `raw.orders` | `order_id` | order_id, customer_id, product_id, quantity, amount, currency, created_at, ingested_at | `ingestion/ingest.py` |
| `raw.products` | `product_id` | product_id, name, category, price, cost, ingested_at | idem |
| `raw.fx_rates` | `(rate_date, base, quote)` | rate_date, base, quote, rate, ingested_at | idem |

## Règles
- Chaque table brute a une colonne `ingested_at` (utilisée par `dbt source freshness`).
- Écriture par upsert sur la clé unique : relancer l'ingestion ne crée jamais de doublons.
- Les contrats dans `contracts/*.yml` (B) décrivent exactement ces tables.
- Les tables de suivi du pipeline sont dans le schéma `ops` (écrit par `orchestration/flow.py`).
