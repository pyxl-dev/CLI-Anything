"""Tests unitaires pour cli-anything-datagouv-mcp."""

import json
import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from cli_anything.datagouv_mcp.core.project import (
    create_session,
    save_session,
    load_session,
    add_to_history,
)
from cli_anything.datagouv_mcp.core.session import (
    create_undo_stack,
    push_state,
    undo,
    redo,
    can_undo,
    can_redo,
)
from cli_anything.datagouv_mcp.utils.formatters import (
    format_size,
    format_dataset_search_results,
    format_dataservice_search_results,
    print_table,
)


# ──── project.py ────


class TestProject:
    def test_create_session(self):
        session = create_session()
        assert "created" in session
        assert "history" in session
        assert session["history"] == []
        assert session["last_results"] is None
        assert session["environment"] == "prod"

    def test_add_to_history(self):
        session = create_session()
        result = {"total": 42, "datasets": []}
        updated = add_to_history(session, "dataset search transport", result)
        assert len(updated["history"]) == 1
        assert updated["last_command"] == "dataset search transport"
        assert updated["last_results"] == result
        # Immutabilité : original non modifié
        assert len(session["history"]) == 0

    def test_add_to_history_multiple(self):
        session = create_session()
        s1 = add_to_history(session, "cmd1", {"total": 1})
        s2 = add_to_history(s1, "cmd2", {"total": 2})
        assert len(s2["history"]) == 2
        assert s2["last_command"] == "cmd2"

    def test_save_load_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "session.json")
            session = create_session()
            session = add_to_history(session, "test", {"total": 5})
            save_session(session, path)
            loaded = load_session(path)
            assert len(loaded["history"]) == 1
            assert "updated" in loaded

    def test_load_session_missing_file(self):
        session = load_session("/tmp/nonexistent_session_file.json")
        assert "created" in session
        assert session["history"] == []

    def test_summarize_result_error(self):
        session = create_session()
        updated = add_to_history(session, "bad", {"error": "Not found"})
        assert "Erreur" in updated["history"][0]["result_summary"]

    def test_summarize_result_title(self):
        session = create_session()
        updated = add_to_history(session, "info", {"title": "Mon Dataset"})
        assert "Mon Dataset" in updated["history"][0]["result_summary"]


# ──── session.py ────


class TestSession:
    def test_create_undo_stack(self):
        stack = create_undo_stack()
        assert stack["undo"] == []
        assert stack["redo"] == []
        assert not can_undo(stack)
        assert not can_redo(stack)

    def test_push_state(self):
        stack = create_undo_stack()
        stack = push_state(stack, {"state": 1})
        assert can_undo(stack)
        assert not can_redo(stack)

    def test_push_clears_redo(self):
        stack = create_undo_stack()
        stack = push_state(stack, {"state": 1})
        stack = push_state(stack, {"state": 2})
        stack, _ = undo(stack)
        assert can_redo(stack)
        stack = push_state(stack, {"state": 3})
        assert not can_redo(stack)

    def test_undo(self):
        stack = create_undo_stack()
        stack = push_state(stack, {"state": 1})
        stack = push_state(stack, {"state": 2})
        stack, restored = undo(stack)
        assert restored == {"state": 2}
        assert can_redo(stack)

    def test_undo_empty(self):
        stack = create_undo_stack()
        stack, restored = undo(stack)
        assert restored is None

    def test_redo(self):
        stack = create_undo_stack()
        stack = push_state(stack, {"state": 1})
        stack, _ = undo(stack)
        stack, restored = redo(stack)
        assert restored == {"state": 1}

    def test_redo_empty(self):
        stack = create_undo_stack()
        stack, restored = redo(stack)
        assert restored is None

    def test_max_size(self):
        stack = create_undo_stack()
        stack = {**stack, "max_size": 3}
        for i in range(10):
            stack = push_state(stack, {"state": i})
        assert len(stack["undo"]) == 3


# ──── formatters.py ────


class TestFormatters:
    def test_format_size_bytes(self):
        assert format_size(500) == "500.0 B"

    def test_format_size_kb(self):
        assert "KB" in format_size(2048)

    def test_format_size_mb(self):
        assert "MB" in format_size(5 * 1024 * 1024)

    def test_format_size_none(self):
        assert format_size(None) == "N/A"

    def test_format_dataset_search_results(self):
        raw = {
            "total": 2,
            "page": 1,
            "page_size": 20,
            "data": [
                {
                    "id": "abc123",
                    "title": "Transport Montpellier",
                    "organization": {"name": "TaM"},
                    "resources": [{"id": "r1"}, {"id": "r2"}],
                    "description": "Données transport",
                },
            ],
        }
        result = format_dataset_search_results(raw)
        assert result["total"] == 2
        assert len(result["datasets"]) == 1
        assert result["datasets"][0]["organization"] == "TaM"
        assert result["datasets"][0]["resources_count"] == 2

    def test_format_dataservice_search_results(self):
        raw = {
            "total": 1,
            "page": 1,
            "page_size": 20,
            "data": [
                {
                    "id": "svc1",
                    "title": "API Adresse",
                    "organization": {"name": "Etalab"},
                    "base_api_url": "https://api-adresse.data.gouv.fr",
                    "description": "Géocodage",
                },
            ],
        }
        result = format_dataservice_search_results(raw)
        assert result["total"] == 1
        assert result["dataservices"][0]["title"] == "API Adresse"

    def test_print_table_empty(self, capsys):
        print_table(["A", "B"], [])
        captured = capsys.readouterr()
        assert "aucun" in captured.out

    def test_print_table_content(self, capsys):
        print_table(["Nom", "Valeur"], [["a", "1"], ["b", "2"]])
        captured = capsys.readouterr()
        assert "Nom" in captured.out
        assert "a" in captured.out


# ──── datagouv_backend.py (mocked) ────


class TestBackendMocked:
    @patch("cli_anything.datagouv_mcp.utils.datagouv_backend._client")
    def test_search_datasets_params(self, mock_client_fn):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [], "total": 0}
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_fn.return_value = mock_client

        from cli_anything.datagouv_mcp.utils.datagouv_backend import search_datasets
        result = search_datasets("transport", page=2, page_size=10)

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "transport" in str(call_args)

    @patch("cli_anything.datagouv_mcp.utils.datagouv_backend._client")
    def test_get_dataset_info_url(self, mock_client_fn):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "abc", "title": "Test"}
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_fn.return_value = mock_client

        from cli_anything.datagouv_mcp.utils.datagouv_backend import get_dataset_info
        result = get_dataset_info("abc123")

        call_url = mock_client.get.call_args[0][0]
        assert "abc123" in call_url
