"""Formatage de sortie pour le CLI data.gouv.fr."""

import json
import sys


def format_size(size_bytes: int | None) -> str:
    """Convertit une taille en bytes en format lisible."""
    if size_bytes is None:
        return "N/A"
    for unit in ("B", "KB", "MB", "GB"):
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def print_output(data: dict, json_mode: bool = False) -> None:
    """Affiche les données en JSON ou format lisible."""
    if json_mode:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    _print_human(data)


def _print_human(data: dict) -> None:
    """Affichage formaté pour les humains."""
    if "error" in data:
        print(f"Erreur : {data['error']}")
        return
    for key, value in data.items():
        if isinstance(value, list):
            print(f"\n{key} ({len(value)}) :")
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    _print_item(item, index=i + 1)
                else:
                    print(f"  {i + 1}. {item}")
        elif isinstance(value, dict):
            print(f"\n{key} :")
            _print_item(value)
        else:
            print(f"{key}: {value}")


def _print_item(item: dict, index: int | None = None, indent: int = 2) -> None:
    """Affiche un élément de dictionnaire formaté."""
    prefix = f"  {index}. " if index else " " * indent
    for k, v in item.items():
        if isinstance(v, list):
            if v and not isinstance(v[0], dict):
                print(f"{prefix}{k}: {', '.join(str(x) for x in v)}")
            else:
                print(f"{prefix}{k}: [{len(v)} éléments]")
        elif isinstance(v, dict):
            print(f"{prefix}{k}: {{...}}")
        else:
            display = str(v)[:120] if isinstance(v, str) else v
            print(f"{prefix}{k}: {display}")
    print()


def print_table(headers: list[str], rows: list[list], max_widths: dict | None = None) -> None:
    """Affiche un tableau formaté."""
    if not rows:
        print("(aucun résultat)")
        return
    col_widths = []
    for i, h in enumerate(headers):
        max_w = len(h)
        for row in rows:
            if i < len(row):
                max_w = max(max_w, len(str(row[i])))
        limit = (max_widths or {}).get(h, 60)
        col_widths.append(min(max_w, limit))
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in col_widths)
    print(header_line)
    print(separator)
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            s = str(cell)[:col_widths[i]].ljust(col_widths[i])
            cells.append(s)
        print(" | ".join(cells))


def format_dataset_search_results(data: dict) -> dict:
    """Formate les résultats de recherche de datasets."""
    results = data.get("data", [])
    return {
        "total": data.get("total", 0),
        "page": data.get("page", 1),
        "page_size": data.get("page_size", 20),
        "datasets": [
            {
                "id": d.get("id", ""),
                "title": d.get("title", ""),
                "organization": (d.get("organization") or {}).get("name", "N/A"),
                "resources_count": len(d.get("resources", [])),
                "description": (d.get("description", "") or "")[:150],
            }
            for d in results
        ],
    }


def format_dataservice_search_results(data: dict) -> dict:
    """Formate les résultats de recherche de dataservices."""
    results = data.get("data", [])
    return {
        "total": data.get("total", 0),
        "page": data.get("page", 1),
        "page_size": data.get("page_size", 20),
        "dataservices": [
            {
                "id": d.get("id", ""),
                "title": d.get("title", ""),
                "organization": (d.get("organization") or {}).get("name", "N/A"),
                "base_api_url": d.get("base_api_url", ""),
                "description": (d.get("description", "") or "")[:150],
            }
            for d in results
        ],
    }
