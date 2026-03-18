"""Commandes dataservices : search, info, openapi-spec."""

from cli_anything.datagouv_mcp.utils.datagouv_backend import (
    search_dataservices as _search,
    get_dataservice_info as _get_info,
    get_dataservice_openapi_spec as _get_spec,
)
from cli_anything.datagouv_mcp.utils.formatters import format_dataservice_search_results


def search(query: str, page: int = 1, page_size: int = 20) -> dict:
    """Recherche de dataservices avec formatage."""
    raw = _search(query, page=page, page_size=page_size)
    return format_dataservice_search_results(raw)


def info(dataservice_id: str) -> dict:
    """Informations détaillées d'un dataservice."""
    raw = _get_info(dataservice_id)
    return {
        "id": raw.get("id", ""),
        "title": raw.get("title", ""),
        "description": (raw.get("description", "") or "")[:500],
        "organization": (raw.get("organization") or {}).get("name", "N/A"),
        "base_api_url": raw.get("base_api_url", ""),
        "documentation_url": raw.get("machine_documentation_url", ""),
        "license": raw.get("license", ""),
        "created_at": raw.get("created_at", ""),
        "last_modified": raw.get("last_modified", ""),
        "tags": raw.get("tags", []),
    }


def openapi_spec(dataservice_id: str) -> dict:
    """Récupère la spécification OpenAPI d'un dataservice."""
    return _get_spec(dataservice_id)
