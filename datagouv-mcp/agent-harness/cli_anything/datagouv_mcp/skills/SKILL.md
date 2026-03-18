---
name: "cli-anything-datagouv-mcp"
description: "CLI pour interroger l'open data français via data.gouv.fr - recherche datasets, requêtes tabulaires, exploration d'APIs publiques"
---

# cli-anything-datagouv-mcp

CLI pour accéder à l'open data français (data.gouv.fr) depuis le terminal.

## Prérequis

- Python >= 3.10
- `pip install -e .` dans le dossier `agent-harness/`
- Connexion internet

## Commandes

### Datasets

```bash
# Rechercher des datasets
cli-anything-datagouv-mcp dataset search "transport"

# Détails d'un dataset
cli-anything-datagouv-mcp dataset info <dataset_id>

# Lister les ressources (fichiers) d'un dataset
cli-anything-datagouv-mcp dataset resources <dataset_id>
```

### Ressources

```bash
# Détails d'une ressource (format, taille, disponibilité tabulaire)
cli-anything-datagouv-mcp resource info <resource_id>

# Requête de données tabulaires (CSV/XLSX sans téléchargement)
cli-anything-datagouv-mcp resource query <resource_id> \
  --filter-column "departement" --filter-value "34" --filter-op contains \
  --sort-column "population" --sort-dir desc \
  --page 1 --page-size 50
```

### Dataservices (APIs publiques)

```bash
# Rechercher des APIs
cli-anything-datagouv-mcp dataservice search "adresse"

# Détails d'une API
cli-anything-datagouv-mcp dataservice info <dataservice_id>

# Spécification OpenAPI (endpoints, paramètres)
cli-anything-datagouv-mcp dataservice openapi-spec <dataservice_id>
```

### Métriques

```bash
# Statistiques d'utilisation (visites, téléchargements par mois)
cli-anything-datagouv-mcp metrics get --dataset-id <id> --limit 6
```

## Sortie JSON

Toutes les commandes supportent `--json` pour une sortie machine-readable :

```bash
cli-anything-datagouv-mcp --json dataset search "transport" | jq '.datasets[0].id'
```

## Mode REPL

```bash
cli-anything-datagouv-mcp  # lance le mode interactif
```

## Workflow typique pour un agent

1. `--json dataset search "mot-clé"` → récupérer la liste et les IDs
2. `--json dataset resources <id>` → trouver les fichiers CSV
3. `--json resource info <resource_id>` → vérifier `tabular_available: true`
4. `--json resource query <resource_id>` → interroger les données
