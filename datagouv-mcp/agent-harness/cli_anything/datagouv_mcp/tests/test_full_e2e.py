"""Tests E2E pour cli-anything-datagouv-mcp - appels API réels + subprocess."""

import json
import os
import subprocess
import sys

import pytest


# ──── Helpers ────


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    import shutil

    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = "cli_anything.datagouv_mcp.datagouv_mcp_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


# Dataset ID connu et stable (Base Sirene des entreprises)
KNOWN_DATASET_ID = "5b7ffc618b4c4169d30727e0"


# ──── Tests API réels ────


class TestRealAPI:
    """Tests avec appels API réels à data.gouv.fr."""

    def test_search_datasets_real(self):
        from cli_anything.datagouv_mcp.core.datasets import search

        result = search("transport", page=1, page_size=5)
        assert result["total"] > 0
        assert len(result["datasets"]) > 0
        assert "id" in result["datasets"][0]
        assert "title" in result["datasets"][0]
        print(f"\n  Trouvé {result['total']} datasets pour 'transport'")

    def test_get_dataset_info_real(self):
        from cli_anything.datagouv_mcp.core.datasets import info

        result = info(KNOWN_DATASET_ID)
        assert result["id"] == KNOWN_DATASET_ID
        assert result["title"] != ""
        assert result["resources_count"] > 0
        print(f"\n  Dataset: {result['title']} ({result['resources_count']} ressources)")

    def test_list_dataset_resources_real(self):
        from cli_anything.datagouv_mcp.core.datasets import resources

        result = resources(KNOWN_DATASET_ID)
        assert len(result["resources"]) > 0
        first = result["resources"][0]
        assert "id" in first
        assert "format" in first
        print(f"\n  {len(result['resources'])} ressources trouvées")

    def test_search_dataservices_real(self):
        from cli_anything.datagouv_mcp.core.dataservices import search

        result = search("adresse", page=1, page_size=5)
        assert result["total"] >= 0
        print(f"\n  Trouvé {result['total']} dataservices pour 'adresse'")

    def test_get_resource_info_real(self):
        """Teste get_resource_info sur une ressource du dataset Sirene."""
        from cli_anything.datagouv_mcp.core.datasets import resources
        from cli_anything.datagouv_mcp.core.resources import info

        res_list = resources(KNOWN_DATASET_ID)
        if res_list["resources"]:
            resource_id = res_list["resources"][0]["id"]
            result = info(resource_id)
            assert result["id"] == resource_id
            assert "format" in result
            print(f"\n  Ressource: {result['title']} ({result['format']})")


# ──── Tests CLI Subprocess ────


class TestCLISubprocess:
    """Tests du CLI installé via subprocess."""

    CLI_BASE = _resolve_cli("cli-anything-datagouv-mcp")

    def _run(self, args, check=True):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            timeout=60,
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "data.gouv.fr" in result.stdout.lower() or "dataset" in result.stdout.lower()

    def test_version(self):
        result = self._run(["--version"])
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_dataset_search_json(self):
        result = self._run(["--json", "dataset", "search", "transport"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "total" in data
        assert "datasets" in data
        print(f"\n  JSON: {data['total']} résultats")

    def test_dataset_info_json(self):
        result = self._run(["--json", "dataset", "info", KNOWN_DATASET_ID])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["id"] == KNOWN_DATASET_ID
        print(f"\n  Dataset: {data.get('title', 'N/A')}")

    def test_dataset_resources_json(self):
        result = self._run(["--json", "dataset", "resources", KNOWN_DATASET_ID])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "resources" in data
        print(f"\n  {len(data['resources'])} ressources")

    def test_unknown_command(self):
        result = self._run(["nonexistent"], check=False)
        assert result.returncode != 0
