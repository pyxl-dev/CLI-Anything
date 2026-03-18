# DATAGOUV-MCP - Agent Harness Analysis

## Software Overview

**Name:** datagouv-mcp
**Type:** MCP Server wrapping data.gouv.fr open data API
**Source:** https://github.com/datagouv/datagouv-mcp
**Backend:** data.gouv.fr REST API (no authentication required)

## Backend Engine

The "backend" is the data.gouv.fr API ecosystem:

| API | Base URL | Purpose |
|-----|----------|---------|
| Main API v1 | `https://www.data.gouv.fr/api/1/` | Dataset/dataservice details |
| Main API v2 | `https://www.data.gouv.fr/api/2/` | Search (datasets, dataservices, resources) |
| Tabular API | `https://tabular-api.data.gouv.fr/api/` | Query CSV/XLSX data without download |
| Metrics API | `https://metric-api.data.gouv.fr/api/` | Usage statistics (prod only) |
| Crawler API | `https://crawler.data.gouv.fr/api/` | Large file exceptions list |

## MCP Tools → CLI Command Mapping

| MCP Tool | CLI Command Group | CLI Subcommand |
|----------|------------------|----------------|
| search_datasets | datasets | search |
| get_dataset_info | datasets | info |
| list_dataset_resources | datasets | resources |
| get_resource_info | resources | info |
| query_resource_data | resources | query |
| search_dataservices | dataservices | search |
| get_dataservice_info | dataservices | info |
| get_dataservice_openapi_spec | dataservices | openapi-spec |
| get_metrics | metrics | get |

## Command Groups

### datasets
- `search <query>` - Search datasets by keywords (paginated)
- `info <dataset_id>` - Get full dataset metadata
- `resources <dataset_id>` - List all files/resources in a dataset

### resources
- `info <resource_id>` - Get resource details + tabular availability
- `query <resource_id>` - Query tabular data with filters and sorting

### dataservices
- `search <query>` - Search external APIs registered on data.gouv.fr
- `info <dataservice_id>` - Get API metadata
- `openapi-spec <dataservice_id>` - Fetch and summarize OpenAPI specification

### metrics
- `get` - Get usage statistics (requires --dataset-id or --resource-id)

## Data Model

**Session State:** Command history, last search results (for interactive reference by index), environment (prod/demo).

**No project files:** Unlike GUI apps, there are no intermediate files to generate. The CLI makes direct API calls and returns structured data.

## Key Differences from GUI CLI Harness

1. **No rendering pipeline** - Data retrieval, not file transformation
2. **No intermediate files** - Direct API calls, not ODF/XML generation
3. **Backend = API** - The "real software" is the data.gouv.fr API itself
4. **Read-only operations** - All tools are queries, no mutations
5. **Network dependency** - Requires internet access to function
