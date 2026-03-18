"""Commandes datasets : search, info, resources."""

from cli_anything.datagouv_mcp.utils.datagouv_backend import (
    search_datasets as _search,
    get_dataset_info as _get_info,
    list_dataset_resources as _list_resources,
)
from cli_anything.datagouv_mcp.utils.formatters import (
    format_dataset_search_results,
    format_size,
)


def search(query: str, page: int = 1, page_size: int = 20) -> dict:
    """Recherche de datasets avec formatage."""
    raw = _search(query, page=page, page_size=page_size)
    return format_dataset_search_results(raw)


def info(dataset_id: str) -> dict:
    """Informations détaillées d'un dataset."""
    raw = _get_info(dataset_id)
    return {
        "id": raw.get("id", ""),
        "title": raw.get("title", ""),
        "description": raw.get("description", ""),
        "organization": (raw.get("organization") or {}).get("name", "N/A"),
        "tags": raw.get("tags", []),
        "license": raw.get("license", ""),
        "frequency": raw.get("frequency", ""),
        "created_at": raw.get("created_at", ""),
        "last_modified": raw.get("last_modified", ""),
        "resources_count": len(raw.get("resources", [])),
        "url": raw.get("page", ""),
    }


def resources(dataset_id: str) -> dict:
    """Liste des ressources d'un dataset."""
    raw = _list_resources(dataset_id)
    return {
        "dataset_id": raw["dataset_id"],
        "dataset_title": raw["title"],
        "resources": [
            {
                **r,
                "filesize_human": format_size(r.get("filesize")),
            }
            for r in raw["resources"]
        ],
    }
