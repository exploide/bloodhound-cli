import click

from bloodhound_cli.api.from_config import api


@click.command()
@click.option("--sid", is_flag=True, help="Show SIDs.")
@click.option("--sep", "-s", metavar="SEP", default="\t", help="Separator between values (default: tab).")
def domains(sid, sep):
    """Get info on domains."""

    for domain in api.domains():
        out = [domain["name"]]
        if sid:
            out.append(domain["id"])
        print(sep.join(out))
