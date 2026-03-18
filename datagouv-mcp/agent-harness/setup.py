"""Configuration du package cli-anything-datagouv-mcp."""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-datagouv-mcp",
    version="1.0.0",
    description="CLI pour interroger l'open data français via data.gouv.fr",
    long_description=open("cli_anything/datagouv_mcp/README.md").read(),
    long_description_content_type="text/markdown",
    author="CLI-Anything",
    python_requires=">=3.10",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    package_data={
        "cli_anything.datagouv_mcp": ["skills/*.md"],
    },
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "httpx>=0.28.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-datagouv-mcp=cli_anything.datagouv_mcp.datagouv_mcp_cli:main",
        ],
    },
)
