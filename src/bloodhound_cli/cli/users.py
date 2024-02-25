import sys

import click

from bloodhound_cli.api.from_config import api
from bloodhound_cli.logger import log


@click.command()
@click.option("--domain", "-d", metavar="DOMAIN", help="Show only users of specific domain.")
@click.option("--enabled", flag_value=True, default=None, help="Show only enabled users.")
@click.option("--sam", is_flag=True, help="Show SAM account name.")
@click.option("--displayname", is_flag=True, help="Show display name.")
@click.option("--description", is_flag=True, help="Show description.")
@click.option("--sep", "-s", metavar="SEP", default="\t", help="Separator between fields (default: tab).")
@click.option("--skip-empty", is_flag=True, help="Skip entry when one field is empty.")
def users(domain, enabled, sam, displayname, description, sep, skip_empty):
    """Get info on users."""

    domainsid = None
    if domain:
        try:
            domainsid = [d["id"] for d in api.domains() if d["name"] == domain.upper()][0]
        except IndexError:
            log.error("Unknown domain %s.", domain)
            sys.exit(1)

    result = api.users(domainsid=domainsid, enabled=enabled)
    result = sorted(result, key=lambda u: (u["properties"].get("domain", "").upper(), (u["properties"].get("name", ""))))

    for user in result:
        props = user["properties"]
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
        if displayname:
            try:
                out.append(props["displayname"])
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
