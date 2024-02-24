import click

from bloodhound_cli.api.from_config import api


@click.command()
@click.option("--domain", "-d", metavar="DOMAIN", help="Show only groups of specific domain.")
@click.option("--sam", is_flag=True, help="Show SAM account name.")
@click.option("--description", is_flag=True, help="Show description.")
@click.option("--sep", "-s", metavar="SEP", default="\t", help="Separator between fields (default: tab).")
@click.option("--skip-empty", is_flag=True, help="Skip entry when one field is empty.")
def groups(domain, sam, description, sep, skip_empty):
    """Get info on groups."""

    if domain:
        domain = domain.upper()
    result = api.groups(domain=domain)
    result = sorted(result, key=lambda u: (u["properties"].get("domain", ""), (u["properties"].get("name", ""))))

    for group in result:
        props = group["properties"]
        try:
            out = [props["name"]]
        except KeyError:
            continue
        if sam:
            try:
                out.append(props["samaccountname"])
            except KeyError:
                if skip_empty:
                    continue
                out.append("")
        if description:
            try:
                out.append(props["description"])
            except KeyError:
                if skip_empty:
                    continue
                out.append("")
        print(sep.join(out))
