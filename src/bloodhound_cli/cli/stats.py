import sys

import click
import prettytable

from bloodhound_cli.api.from_config import api
from bloodhound_cli.constants import RID
from bloodhound_cli.logger import log
from .paramtypes import DomainType


@click.command()
@click.option("--domain", "-d", type=DomainType(), help="Show stats for specific domain.")
def stats(domain):
    """Get statistics on domains."""

    domains = sorted((d["name"], d["id"]) for d in api.domains(collected=True))
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

        row = ["User Accounts"]
        result = api.users(domainsid=domsid)
        row.append(len(result))
        result = [u for u in result if u["properties"].get("enabled", "")]
        row.append(len(result))
        table.add_row(row)

        row = ["Computer Accounts"]
        result = api.computers(domainsid=domsid)
        row.append(len(result))
        result = [c for c in result if c["properties"].get("enabled", "")]
        row.append(len(result))
        table.add_row(row)

        row = ["Domain Admins"]
        result = api.group_members(f"{domsid}-{RID.DOMAIN_ADMINS}", kind="User")
        row.append(len(result))
        result = [u for u in result if u["properties"].get("enabled", "")]
        row.append(len(result))
        table.add_row(row)

        row = ["Domain Controllers"]
        result = api.group_members(f"{domsid}-{RID.DOMAIN_CONTROLLERS}", kind="Computer")
        row.append(len(result))
        result = [c for c in result if c["properties"].get("enabled", "")]
        row.append(len(result))
        table.add_row(row)

        row = ["Protected Users"]
        result = api.group_members(f"{domsid}-{RID.PROTECTED_USERS}", kind="User")
        row.append(len(result))
        result = [u for u in result if u["properties"].get("enabled", "")]
        row.append(len(result))
        table.add_row(row)

        row = ["Groups"]
        result = api.groups(domainsid=domsid)
        row.append(len(result))
        row.append("")
        table.add_row(row)

        row = ["Root CAs"]
        result = api.root_cas(domainsid=domsid)
        row.append(len(result))
        row.append("")
        table.add_row(row)

        row = ["Enterprise CAs"]
        result = api.enterprise_cas(domainsid=domsid)
        row.append(len(result))
        row.append("")
        table.add_row(row)

        row = ["Cert Templates"]
        result = api.cert_templates(domainsid=domsid)
        row.append(len(result))
        row.append("")
        table.add_row(row)

        print(table)
