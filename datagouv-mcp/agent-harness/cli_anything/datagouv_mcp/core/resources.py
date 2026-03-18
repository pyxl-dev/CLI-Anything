"""Commandes resources : info, query."""

from cli_anything.datagouv_mcp.utils.datagouv_backend import (
    get_resource_info as _get_info,
    query_resource_data as _query,
)
from cli_anything.datagouv_mcp.utils.formatters import format_size


def info(resource_id: str) -> dict:
    """Informations détaillées d'une ressource."""
    raw = _get_info(resource_id)
    return {
        "id": raw.get("id", ""),
        "title": raw.get("title", ""),
        "format": raw.get("format", ""),
        "filesize": raw.get("filesize"),
        "filesize_human": format_size(raw.get("filesize")),
        "mime": raw.get("mime", ""),
        "type": raw.get("type", ""),
        "url": raw.get("url", ""),
        "description": raw.get("description", ""),
        "dataset_id": raw.get("dataset", {}).get("id", "") if isinstance(raw.get("dataset"), dict) else raw.get("dataset_id", ""),
        "tabular_available": raw.get("tabular_available", False),
    }


def query(
    resource_id: str,
    page: int = 1,
    page_size: int = 20,
    filter_column: str | None = None,
    filter_value: str | None = None,
    filter_operator: str = "exact",
    sort_column: str | None = None,
    sort_direction: str = "asc",
) -> dict:
    """Requête de données tabulaires."""
    raw = _query(
        resource_id,
        page=page,
        page_size=page_size,
        filter_column=filter_column,
        filter_value=filter_value,
        filter_operator=filter_operator,
        sort_column=sort_column,
        sort_direction=sort_direction,
    )
    data = raw.get("data", [])
    meta = raw.get("meta", {})
    return {
        "resource_id": resource_id,
        "total": meta.get("total", len(data)),
        "page": meta.get("page", page),
        "page_size": meta.get("page_size", page_size),
        "columns": list(data[0].keys()) if data else [],
        "rows_count": len(data),
        "data": data,
    }
