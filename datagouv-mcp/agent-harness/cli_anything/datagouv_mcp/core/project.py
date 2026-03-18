"""Gestion de l'état de session CLI."""

import json
import os
from datetime import datetime, timezone


def create_session(session_path: str | None = None) -> dict:
    """Crée une nouvelle session CLI."""
    return {
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "history": [],
        "last_results": None,
        "last_command": None,
        "environment": "prod",
    }


def save_session(session: dict, path: str) -> None:
    """Sauvegarde la session sur disque."""
    import fcntl
    updated = {**session, "updated": datetime.now(timezone.utc).isoformat()}
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    try:
        f = open(path, "r+")
    except FileNotFoundError:
        f = open(path, "w")
    with f:
        locked = False
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            locked = True
        except (ImportError, OSError):
            pass
        try:
            f.seek(0)
            f.truncate()
            json.dump(updated, f, ensure_ascii=False, indent=2)
            f.flush()
        finally:
            if locked:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def load_session(path: str) -> dict:
    """Charge une session depuis le disque."""
    if not os.path.exists(path):
        return create_session()
    with open(path) as f:
        return json.load(f)


def add_to_history(session: dict, command: str, result: dict) -> dict:
    """Ajoute une commande à l'historique (immutable)."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "result_summary": _summarize_result(result),
    }
    return {
        **session,
        "history": [*session.get("history", []), entry],
        "last_command": command,
        "last_results": result,
    }


def _summarize_result(result: dict) -> str:
    """Résumé court d'un résultat pour l'historique."""
    if "error" in result:
        return f"Erreur : {result['error'][:80]}"
    if "total" in result:
        return f"{result['total']} résultats"
    if "title" in result:
        return str(result["title"])[:80]
    return f"{len(result)} clés"
