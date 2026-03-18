# TEST.md - Plan de tests cli-anything-datagouv-mcp

## Test Inventory Plan

- `test_core.py` : ~20 tests unitaires (données synthétiques, API mockée)
- `test_full_e2e.py` : ~12 tests E2E (appels API réels + subprocess)

## Unit Test Plan (test_core.py)

### core/project.py
- `test_create_session` : crée une session avec les champs requis
- `test_add_to_history` : ajoute une entrée à l'historique (immutable)
- `test_save_load_session` : round-trip sauvegarde/chargement
- `test_summarize_result_error` : résumé d'un résultat d'erreur
- `test_summarize_result_total` : résumé avec total
- **Edge cases** : session vide, chemin inexistant

### core/session.py
- `test_create_undo_stack` : pile vide initialement
- `test_push_state` : empile un état, vide redo
- `test_undo` : dépile et restaure
- `test_redo` : rétablit un état
- `test_undo_empty` : undo sur pile vide retourne None
- `test_redo_empty` : redo sur pile vide retourne None
- `test_max_size` : pile limitée à max_size entrées

### utils/formatters.py
- `test_format_size` : conversion bytes → lisible
- `test_format_size_none` : None → "N/A"
- `test_print_table` : tableau formaté
- `test_format_dataset_search_results` : formatage résultats recherche
- `test_format_dataservice_search_results` : formatage résultats recherche

### utils/datagouv_backend.py (mocked)
- `test_search_datasets_mock` : mock httpx, vérifie paramètres
- `test_get_dataset_info_mock` : mock httpx, vérifie URL

## E2E Test Plan (test_full_e2e.py)

### Appels API réels
- `test_search_datasets_real` : recherche "transport" retourne des résultats
- `test_get_dataset_info_real` : info sur un dataset connu
- `test_list_dataset_resources_real` : liste les ressources
- `test_search_dataservices_real` : recherche "adresse" retourne des résultats
- `test_get_resource_info_real` : info sur une ressource connue
- `test_query_resource_data_real` : requête tabulaire sur une ressource CSV connue

### Subprocess Tests (TestCLISubprocess)
- `test_help` : --help retourne code 0
- `test_version` : --version affiche la version
- `test_dataset_search_json` : --json dataset search retourne du JSON valide
- `test_dataset_info_json` : --json dataset info retourne du JSON valide
- `test_resource_query_json` : --json resource query retourne du JSON valide
- `test_unknown_command` : commande inconnue retourne code non-0

## Realistic Workflow Scenarios

### Workflow 1 : Exploration de données transport
**Simule :** Un data analyst cherchant des données de transport
**Opérations :**
1. `dataset search "transport"` → trouver des datasets
2. `dataset info <id>` → examiner un dataset
3. `dataset resources <id>` → lister les fichiers
4. `resource info <id>` → vérifier si tabulaire
5. `resource query <id>` → interroger les données
**Vérifié :** Chaque étape retourne des données structurées, IDs cohérents entre étapes

### Workflow 2 : Découverte d'APIs
**Simule :** Un développeur cherchant des APIs publiques
**Opérations :**
1. `dataservice search "adresse"` → trouver des APIs
2. `dataservice info <id>` → examiner une API
3. `dataservice openapi-spec <id>` → lire la spec
**Vérifié :** Spec OpenAPI parsée correctement, endpoints listés

---

## Test Results

```
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.0.2, pluggy-1.6.0

cli_anything/datagouv_mcp/tests/test_core.py::TestProject::test_create_session PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestProject::test_add_to_history PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestProject::test_add_to_history_multiple PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestProject::test_save_load_session PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestProject::test_load_session_missing_file PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestProject::test_summarize_result_error PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestProject::test_summarize_result_title PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestSession::test_create_undo_stack PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestSession::test_push_state PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestSession::test_push_clears_redo PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestSession::test_undo PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestSession::test_undo_empty PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestSession::test_redo PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestSession::test_redo_empty PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestSession::test_max_size PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestFormatters::test_format_size_bytes PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestFormatters::test_format_size_kb PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestFormatters::test_format_size_mb PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestFormatters::test_format_size_none PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestFormatters::test_format_dataset_search_results PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestFormatters::test_format_dataservice_search_results PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestFormatters::test_print_table_empty PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestFormatters::test_print_table_content PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestBackendMocked::test_search_datasets_params PASSED
cli_anything/datagouv_mcp/tests/test_core.py::TestBackendMocked::test_get_dataset_info_url PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestRealAPI::test_search_datasets_real PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestRealAPI::test_get_dataset_info_real PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestRealAPI::test_list_dataset_resources_real PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestRealAPI::test_search_dataservices_real PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestRealAPI::test_get_resource_info_real PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestCLISubprocess::test_help PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestCLISubprocess::test_version PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestCLISubprocess::test_dataset_search_json PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestCLISubprocess::test_dataset_info_json PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestCLISubprocess::test_dataset_resources_json PASSED
cli_anything/datagouv_mcp/tests/test_full_e2e.py::TestCLISubprocess::test_unknown_command PASSED

============================== 36 passed in 3.96s ==============================
```

### Summary Statistics
- **Total tests:** 36
- **Passed:** 36 (100%)
- **Failed:** 0
- **Execution time:** 3.96s
- **CLI resolution:** `[_resolve_cli] Using installed command` (CLI_ANYTHING_FORCE_INSTALLED=1)

### Coverage Notes
- Unit tests cover project.py, session.py, formatters.py, and mocked backend
- E2E tests hit the real data.gouv.fr API (datasets, dataservices, resources)
- Subprocess tests verify the installed CLI command (--help, --version, --json output)
- Not covered: query_resource_data E2E (requires knowing a tabular-available resource ID), metrics (prod-only API), dataservice openapi-spec E2E
