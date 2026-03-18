"""Backend HTTP client pour l'API data.gouv.fr."""

import httpx

API_V1 = "https://www.data.gouv.fr/api/1"
API_V2 = "https://www.data.gouv.fr/api/2"
TABULAR_API = "https://tabular-api.data.gouv.fr/api"
METRICS_API = "https://metric-api.data.gouv.fr/api"

USER_AGENT = "cli-anything-datagouv-mcp/1.0.0"
TIMEOUT = 30.0


def _client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
        follow_redirects=True,
    )


def search_datasets(query: str, page: int = 1, page_size: int = 20) -> dict:
    """Recherche de datasets par mots-clés."""
    with _client() as client:
        resp = client.get(f"{API_V2}/datasets/search/", params={
            "q": query, "page": page, "page_size": min(page_size, 100),
        })
        resp.raise_for_status()
        return resp.json()


def get_dataset_info(dataset_id: str) -> dict:
    """Métadonnées détaillées d'un dataset."""
    with _client() as client:
        resp = client.get(f"{API_V1}/datasets/{dataset_id}/")
        resp.raise_for_status()
        return resp.json()


def list_dataset_resources(dataset_id: str) -> dict:
    """Liste des ressources (fichiers) d'un dataset."""
    with _client() as client:
        resp = client.get(f"{API_V1}/datasets/{dataset_id}/")
        resp.raise_for_status()
        data = resp.json()
        return {
            "dataset_id": dataset_id,
            "title": data.get("title", ""),
            "resources": [
                {
                    "id": r.get("id", ""),
                    "title": r.get("title", ""),
                    "format": r.get("format", ""),
                    "filesize": r.get("filesize"),
                    "mime": r.get("mime", ""),
                    "url": r.get("url", ""),
                    "type": r.get("type", ""),
                }
                for r in data.get("resources", [])
            ],
        }


def get_resource_info(resource_id: str) -> dict:
    """Informations détaillées d'une ressource."""
    with _client() as client:
        resp = client.get(f"{API_V2}/datasets/resources/{resource_id}/")
        resp.raise_for_status()
        wrapper = resp.json()
        # L'API v2 retourne {"resource": {...}, "dataset_id": "..."}
        data = wrapper.get("resource", wrapper)
        data["dataset_id"] = wrapper.get("dataset_id", "")
        # Check tabular availability
        tabular_available = False
        try:
            tab_resp = client.get(f"{TABULAR_API}/resources/{resource_id}/profile/")
            tabular_available = tab_resp.status_code == 200
        except httpx.HTTPError:
            pass
        data["tabular_available"] = tabular_available
        return data


def query_resource_data(
    resource_id: str,
    page: int = 1,
    page_size: int = 20,
    filter_column: str | None = None,
    filter_value: str | None = None,
    filter_operator: str = "exact",
    sort_column: str | None = None,
    sort_direction: str = "asc",
) -> dict:
    """Requête de données tabulaires (CSV/XLSX) via le Tabular API."""
    params: dict = {"page": page, "page_size": min(page_size, 200)}
    if filter_column and filter_value:
        params[f"{filter_column}__{filter_operator}"] = filter_value
    if sort_column:
        params[f"{sort_column}__sort"] = sort_direction
    with _client() as client:
        resp = client.get(f"{TABULAR_API}/resources/{resource_id}/data/", params=params)
        resp.raise_for_status()
        return resp.json()


def search_dataservices(query: str, page: int = 1, page_size: int = 20) -> dict:
    """Recherche d'APIs externes enregistrées sur data.gouv.fr."""
    with _client() as client:
        resp = client.get(f"{API_V2}/dataservices/search/", params={
            "q": query, "page": page, "page_size": min(page_size, 100),
        })
        resp.raise_for_status()
        return resp.json()


def get_dataservice_info(dataservice_id: str) -> dict:
    """Métadonnées détaillées d'un dataservice."""
    with _client() as client:
        resp = client.get(f"{API_V1}/dataservices/{dataservice_id}/")
        resp.raise_for_status()
        return resp.json()


def get_dataservice_openapi_spec(dataservice_id: str) -> dict:
    """Récupère et résume la spécification OpenAPI d'un dataservice."""
    import yaml
    with _client() as client:
        # Get dataservice info first to find spec URL
        info_resp = client.get(f"{API_V1}/dataservices/{dataservice_id}/")
        info_resp.raise_for_status()
        info = info_resp.json()
        spec_url = info.get("machine_documentation_url")
        if not spec_url:
            return {"error": "Pas de spécification OpenAPI disponible", "dataservice_id": dataservice_id}
        # Fetch the spec
        spec_resp = client.get(spec_url)
        spec_resp.raise_for_status()
        content_type = spec_resp.headers.get("content-type", "")
        if "yaml" in content_type or spec_url.endswith((".yaml", ".yml")):
            spec = yaml.safe_load(spec_resp.text)
        else:
            spec = spec_resp.json()
        return _summarize_spec(spec, spec_url)


def _summarize_spec(spec: dict, spec_url: str) -> dict:
    """Résume une spécification OpenAPI."""
    info = spec.get("info", {})
    servers = spec.get("servers", [])
    paths = spec.get("paths", {})
    endpoints = []
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                params = []
                for p in details.get("parameters", []):
                    params.append({
                        "name": p.get("name", ""),
                        "in": p.get("in", ""),
                        "required": p.get("required", False),
                        "type": p.get("schema", {}).get("type", ""),
                    })
                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary", details.get("description", "")[:100]),
                    "parameters": params,
                })
    return {
        "spec_url": spec_url,
        "title": info.get("title", ""),
        "version": info.get("version", ""),
        "description": (info.get("description", "") or "")[:300],
        "servers": [s.get("url", "") for s in servers],
        "endpoints_count": len(endpoints),
        "endpoints": endpoints,
    }


def get_metrics(
    dataset_id: str | None = None,
    resource_id: str | None = None,
    limit: int = 12,
) -> dict:
    """Statistiques d'utilisation (visites, téléchargements)."""
    if not dataset_id and not resource_id:
        return {"error": "Au moins dataset_id ou resource_id requis"}
    params: dict = {"limit": min(limit, 100)}
    if dataset_id:
        endpoint = f"{METRICS_API}/datasets/{dataset_id}/"
    else:
        endpoint = f"{METRICS_API}/resources/{resource_id}/"
    with _client() as client:
        resp = client.get(endpoint, params=params)
        resp.raise_for_status()
        return resp.json()
