import sys

import click
import prettytable

from bloodhound_cli.api.from_config import api
from bloodhound_cli.constants import RID
from bloodhound_cli.logger import log


@click.command()
@click.option("--domain", "-d", metavar="DOMAIN", help="Show stats for specific domain.")
def stats(domain):
    """Get statistics on domain objects."""

    domains = sorted((d["name"], d["id"]) for d in api.domains())
    if domain:
        domains = [d for d in domains if d[0] == domain.upper()]
        if not domains:
            log.error("Unknown domain %s.", domain)
            sys.exit(1)

    for dom, domsid in domains:
        table = prettytable.PrettyTable()
        table.set_style(prettytable.SINGLE_BORDER)
        table.field_names = [dom, "  all  ", "enabled"]
        table.align[dom] = "l"
        table.align["  all  "] = "r"
        table.align["enabled"] = "r"

        row = ["User accounts"]
        result = api.users(domainsid=domsid)
        row.append(len(result))
        result = [u for u in result if u["properties"].get("enabled", "")]
        row.append(len(result))
        table.add_row(row)

        row = ["Computer accounts"]
        result = api.computers(domainsid=domsid)
        row.append(len(result))
        result = [c for c in result if c["properties"].get("enabled", "")]
        row.append(len(result))
        table.add_row(row)

        row = ["Domain admins"]
        result = api.group_members(f"{domsid}-{RID.DOMAIN_ADMINS}", kind="User")
        row.append(len(result))
        result = [u for u in result if u["properties"].get("enabled", "")]
        row.append(len(result))
        table.add_row(row)

        row = ["Domain controllers"]
        result = api.group_members(f"{domsid}-{RID.DOMAIN_CONTROLLERS}", kind="Computer")
        row.append(len(result))
        result = [c for c in result if c["properties"].get("enabled", "")]
        row.append(len(result))
        table.add_row(row)

        row = ["Groups"]
        result = api.groups(domainsid=domsid)
        row.append(len(result))
        row.append("")
        table.add_row(row)

        print(table)
