import click

from bloodhound_cli.api.from_config import api


@click.command()
@click.option("--domain", "-d", metavar="DOMAIN", help="Show only computers of specific domain.")
@click.option("--enabled", flag_value=True, default=None, help="Show only enabled computers.")
@click.option("--sam", is_flag=True, help="Show SAM-Account-Name.")
@click.option("--pre-win2k-pw", is_flag=True, help="Show pre-win2k password candidate.")
@click.option("--description", is_flag=True, help="Show description.")
@click.option("--sep", "-s", metavar="SEP", default="\t", help="Separator between fields (default: tab).")
@click.option("--skip-empty", is_flag=True, help="Skip entry when one field is empty.")
def computers(domain, enabled, sam, pre_win2k_pw, description, sep, skip_empty):
    """Get info on computers."""

    if domain:
        domain = domain.upper()
    result = api.computers(domain=domain, enabled=enabled)
    result = sorted(result, key=lambda c: (c["properties"].get("domain", ""), (c["properties"].get("name", ""))))

    for computer in result:
        props = computer["properties"]
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
        if pre_win2k_pw:
            try:
                out.append(props["samaccountname"].strip().rstrip("$").lower()[:14])
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
