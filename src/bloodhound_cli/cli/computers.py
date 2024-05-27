import sys

import click

from bloodhound_cli.api.from_config import api
from bloodhound_cli.logger import log


@click.command()
@click.option("--domain", "-d", metavar="DOMAIN", help="Show only computers of specific domain.")
@click.option("--enabled", flag_value=True, default=None, help="Show only enabled computers.")
@click.option("--owned", flag_value=True, default=None, help="Show only computers marked as owned.")
@click.option("--sam", is_flag=True, help="Show SAM account name.")
@click.option("--pre-win2k-pw", is_flag=True, help="Show pre-win2k password candidate.")
@click.option("--description", is_flag=True, help="Show description.")
@click.option("--sep", "-s", metavar="SEP", default="\t", help="Separator between fields (default: tab).")
@click.option("--skip-empty", is_flag=True, help="Skip entry when one field is empty.")
def computers(domain, enabled, owned, sam, pre_win2k_pw, description, sep, skip_empty):
    """Get lists of computers."""

    domainsid = None
    if domain:
        try:
            domainsid = [d["id"] for d in api.domains() if d["name"] == domain.upper()][0]
        except IndexError:
            log.error("Unknown domain %s.", domain)
            sys.exit(1)

    result = api.computers(domainsid=domainsid, enabled=enabled)
    result = sorted(result, key=lambda c: (c["properties"].get("domain", "").upper(), (c["properties"].get("name", ""))))

    for computer in result:
        props = computer["properties"]
        if owned is True:
            if "owned" not in props.get("system_tags", "").split():
                continue
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
