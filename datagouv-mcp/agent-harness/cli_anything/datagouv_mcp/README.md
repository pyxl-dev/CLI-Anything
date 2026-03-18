# cli-anything-datagouv-mcp

CLI pour interroger l'open data français via l'API data.gouv.fr.

## Prérequis

- Python >= 3.10
- Connexion internet (appels API data.gouv.fr)

## Installation

```bash
cd datagouv-mcp/agent-harness
pip install -e .
```

## Utilisation

### Mode commande

```bash
# Rechercher des datasets
cli-anything-datagouv-mcp dataset search "transport"

# Détails d'un dataset
cli-anything-datagouv-mcp dataset info <dataset_id>

# Lister les fichiers d'un dataset
cli-anything-datagouv-mcp dataset resources <dataset_id>

# Informations sur une ressource
cli-anything-datagouv-mcp resource info <resource_id>

# Requête de données tabulaires
cli-anything-datagouv-mcp resource query <resource_id> --page 1 --page-size 10

# Rechercher des APIs
cli-anything-datagouv-mcp dataservice search "adresse"

# Détails d'une API
cli-anything-datagouv-mcp dataservice info <dataservice_id>

# Spécification OpenAPI
cli-anything-datagouv-mcp dataservice openapi-spec <dataservice_id>

# Statistiques d'utilisation
cli-anything-datagouv-mcp metrics get --dataset-id <dataset_id>
```

### Mode JSON

Ajouter `--json` pour obtenir une sortie machine-readable :

```bash
cli-anything-datagouv-mcp --json dataset search "transport"
```

### Mode REPL

Lancer sans argument pour le mode interactif :

```bash
cli-anything-datagouv-mcp
```

## Tests

```bash
cd datagouv-mcp/agent-harness
pip install -e .
pytest cli_anything/datagouv_mcp/tests/ -v -s
```

## Architecture

Le CLI appelle directement l'API data.gouv.fr via httpx. Pas de dépendance au serveur MCP.

```
cli_anything/datagouv_mcp/
├── datagouv_mcp_cli.py    # Point d'entrée CLI (Click + REPL)
├── core/                   # Logique métier
│   ├── datasets.py         # search, info, resources
│   ├── dataservices.py     # search, info, openapi-spec
│   ├── resources.py        # info, query
│   ├── metrics.py          # get
│   ├── project.py          # Gestion de session
│   └── session.py          # Pile undo/redo
└── utils/
    ├── datagouv_backend.py # Client HTTP data.gouv.fr
    ├── formatters.py       # Formatage sortie (table/JSON)
    └── repl_skin.py        # Interface REPL unifiée
```
