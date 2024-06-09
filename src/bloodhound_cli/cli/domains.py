import click

from bloodhound_cli.api.from_config import api


@click.command()
@click.option("--collected/--not-collected", default=None, help="Show only (not) collected domains.")
@click.option("--sid", is_flag=True, help="Show SIDs.")
@click.option("--sep", "-s", metavar="SEP", default="\t", help="Separator between fields (default: tab).")
def domains(collected, sid, sep):
    """Get lists of domains."""

    result = api.domains()
    result = sorted(result, key=lambda d: d["name"])

    for domain in result:
        if collected is not None and collected != domain.get("collected", False):
            continue
        out = [domain["name"]]
        if sid:
            out.append(domain["id"])
        print(sep.join(out))
