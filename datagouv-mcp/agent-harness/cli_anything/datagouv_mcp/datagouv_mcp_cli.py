"""CLI data.gouv.fr - Interface en ligne de commande pour l'open data français."""

import click
import json
import sys

from cli_anything.datagouv_mcp import __version__
from cli_anything.datagouv_mcp.core import datasets, dataservices, resources as resources_mod, metrics as metrics_mod
from cli_anything.datagouv_mcp.core.project import create_session, add_to_history
from cli_anything.datagouv_mcp.utils.formatters import print_output, print_table


class Context:
    """Contexte partagé entre commandes."""
    def __init__(self, json_mode: bool = False):
        self.json_mode = json_mode
        self.session = create_session()


pass_ctx = click.make_pass_decorator(Context, ensure=True)


@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Sortie JSON machine-readable")
@click.option("--version", is_flag=True, help="Affiche la version")
@click.pass_context
def cli(ctx, json_mode, version):
    """CLI data.gouv.fr - Accès en ligne de commande à l'open data français."""
    ctx.ensure_object(Context)
    ctx.obj.json_mode = json_mode
    if version:
        click.echo(f"cli-anything-datagouv-mcp {__version__}")
        return
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ──── DATASETS ────

@cli.group()
@pass_ctx
def dataset(ctx):
    """Recherche et exploration de datasets."""
    pass


@dataset.command("search")
@click.argument("query")
@click.option("--page", default=1, type=int, help="Numéro de page")
@click.option("--page-size", default=20, type=int, help="Résultats par page (max 100)")
@pass_ctx
def dataset_search(ctx, query, page, page_size):
    """Recherche de datasets par mots-clés."""
    result = datasets.search(query, page=page, page_size=page_size)
    ctx.session = add_to_history(ctx.session, f"dataset search {query}", result)
    if ctx.json_mode:
        print_output(result, json_mode=True)
    else:
        click.echo(f"\n{result['total']} datasets trouvés (page {result['page']}) :\n")
        rows = [
            [d["id"][:8], d["title"][:50], d["organization"][:25], str(d["resources_count"])]
            for d in result["datasets"]
        ]
        print_table(["ID", "Titre", "Organisation", "Fichiers"], rows)


@dataset.command("info")
@click.argument("dataset_id")
@pass_ctx
def dataset_info(ctx, dataset_id):
    """Métadonnées détaillées d'un dataset."""
    result = datasets.info(dataset_id)
    ctx.session = add_to_history(ctx.session, f"dataset info {dataset_id}", result)
    print_output(result, json_mode=ctx.json_mode)


@dataset.command("resources")
@click.argument("dataset_id")
@pass_ctx
def dataset_resources(ctx, dataset_id):
    """Liste des fichiers/ressources d'un dataset."""
    result = datasets.resources(dataset_id)
    ctx.session = add_to_history(ctx.session, f"dataset resources {dataset_id}", result)
    if ctx.json_mode:
        print_output(result, json_mode=True)
    else:
        click.echo(f"\nRessources de '{result['dataset_title']}' :\n")
        rows = [
            [r["id"][:8], r["title"][:40], r["format"], r["filesize_human"]]
            for r in result["resources"]
        ]
        print_table(["ID", "Titre", "Format", "Taille"], rows)


# ──── DATASERVICES ────

@cli.group()
@pass_ctx
def dataservice(ctx):
    """Recherche et exploration d'APIs externes."""
    pass


@dataservice.command("search")
@click.argument("query")
@click.option("--page", default=1, type=int, help="Numéro de page")
@click.option("--page-size", default=20, type=int, help="Résultats par page (max 100)")
@pass_ctx
def dataservice_search(ctx, query, page, page_size):
    """Recherche d'APIs externes par mots-clés."""
    result = dataservices.search(query, page=page, page_size=page_size)
    ctx.session = add_to_history(ctx.session, f"dataservice search {query}", result)
    if ctx.json_mode:
        print_output(result, json_mode=True)
    else:
        click.echo(f"\n{result['total']} dataservices trouvés (page {result['page']}) :\n")
        rows = [
            [d["id"][:8], d["title"][:40], d["organization"][:25], d["base_api_url"][:30]]
            for d in result["dataservices"]
        ]
        print_table(["ID", "Titre", "Organisation", "URL API"], rows)


@dataservice.command("info")
@click.argument("dataservice_id")
@pass_ctx
def dataservice_info(ctx, dataservice_id):
    """Métadonnées détaillées d'un dataservice."""
    result = dataservices.info(dataservice_id)
    ctx.session = add_to_history(ctx.session, f"dataservice info {dataservice_id}", result)
    print_output(result, json_mode=ctx.json_mode)


@dataservice.command("openapi-spec")
@click.argument("dataservice_id")
@pass_ctx
def dataservice_openapi_spec(ctx, dataservice_id):
    """Récupère la spécification OpenAPI d'un dataservice."""
    result = dataservices.openapi_spec(dataservice_id)
    ctx.session = add_to_history(ctx.session, f"dataservice openapi-spec {dataservice_id}", result)
    print_output(result, json_mode=ctx.json_mode)


# ──── RESOURCES ────

@cli.group()
@pass_ctx
def resource(ctx):
    """Informations et requêtes sur les ressources."""
    pass


@resource.command("info")
@click.argument("resource_id")
@pass_ctx
def resource_info(ctx, resource_id):
    """Informations détaillées d'une ressource."""
    result = resources_mod.info(resource_id)
    ctx.session = add_to_history(ctx.session, f"resource info {resource_id}", result)
    print_output(result, json_mode=ctx.json_mode)


@resource.command("query")
@click.argument("resource_id")
@click.option("--page", default=1, type=int, help="Numéro de page")
@click.option("--page-size", default=20, type=int, help="Lignes par page (max 200)")
@click.option("--filter-column", default=None, help="Colonne à filtrer")
@click.option("--filter-value", default=None, help="Valeur du filtre")
@click.option("--filter-op", default="exact", type=click.Choice(["exact", "contains", "less", "greater"]), help="Opérateur")
@click.option("--sort-column", default=None, help="Colonne de tri")
@click.option("--sort-dir", default="asc", type=click.Choice(["asc", "desc"]), help="Direction du tri")
@pass_ctx
def resource_query(ctx, resource_id, page, page_size, filter_column, filter_value, filter_op, sort_column, sort_dir):
    """Requête de données tabulaires (CSV/XLSX)."""
    result = resources_mod.query(
        resource_id, page=page, page_size=page_size,
        filter_column=filter_column, filter_value=filter_value, filter_operator=filter_op,
        sort_column=sort_column, sort_direction=sort_dir,
    )
    ctx.session = add_to_history(ctx.session, f"resource query {resource_id}", result)
    if ctx.json_mode:
        print_output(result, json_mode=True)
    else:
        click.echo(f"\n{result['total']} lignes (page {result['page']}, {result['rows_count']} affichées) :\n")
        if result["data"]:
            headers = result["columns"][:8]  # Limit columns for readability
            rows = [[str(row.get(h, ""))[:30] for h in headers] for row in result["data"][:50]]
            print_table(headers, rows)


# ──── METRICS ────

@cli.group()
@pass_ctx
def metrics(ctx):
    """Statistiques d'utilisation."""
    pass


@metrics.command("get")
@click.option("--dataset-id", default=None, help="ID du dataset")
@click.option("--resource-id", default=None, help="ID de la ressource")
@click.option("--limit", default=12, type=int, help="Nombre de mois (max 100)")
@pass_ctx
def metrics_get(ctx, dataset_id, resource_id, limit):
    """Statistiques de visites et téléchargements."""
    result = metrics_mod.get(dataset_id=dataset_id, resource_id=resource_id, limit=limit)
    ctx.session = add_to_history(ctx.session, f"metrics get", result)
    print_output(result, json_mode=ctx.json_mode)


# ──── REPL ────

@cli.command(hidden=True)
@pass_ctx
def repl(ctx):
    """Mode interactif REPL."""
    from cli_anything.datagouv_mcp.utils.repl_skin import ReplSkin

    skin = ReplSkin("datagouv-mcp", version=__version__)
    skin.print_banner()

    commands = {
        "dataset search <query>": "Recherche de datasets",
        "dataset info <id>": "Détails d'un dataset",
        "dataset resources <id>": "Fichiers d'un dataset",
        "dataservice search <query>": "Recherche d'APIs",
        "dataservice info <id>": "Détails d'une API",
        "dataservice openapi-spec <id>": "Spécification OpenAPI",
        "resource info <id>": "Détails d'une ressource",
        "resource query <id>": "Données tabulaires",
        "metrics get --dataset-id <id>": "Statistiques",
        "help": "Afficher cette aide",
        "exit / quit": "Quitter",
    }

    pt_session = skin.create_prompt_session()
    while True:
        try:
            line = skin.get_input(pt_session, project_name="data.gouv.fr")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break
        if not line:
            continue
        stripped = line.strip()
        if stripped in ("exit", "quit", "q"):
            skin.print_goodbye()
            break
        if stripped == "help":
            skin.help(commands)
            continue
        # Parse and dispatch to Click commands
        try:
            args = stripped.split()
            if ctx.json_mode:
                args = ["--json"] + args
            cli.main(args=args, standalone_mode=False)
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except SystemExit:
            pass
        except Exception as e:
            skin.error(f"Erreur : {e}")


def main():
    """Point d'entrée principal."""
    cli(obj=Context())


if __name__ == "__main__":
    main()
