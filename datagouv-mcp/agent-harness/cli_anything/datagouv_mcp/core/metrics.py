"""Commandes metrics : get."""

from cli_anything.datagouv_mcp.utils.datagouv_backend import get_metrics as _get_metrics


def get(
    dataset_id: str | None = None,
    resource_id: str | None = None,
    limit: int = 12,
) -> dict:
    """Récupère les statistiques d'utilisation."""
    return _get_metrics(dataset_id=dataset_id, resource_id=resource_id, limit=limit)
