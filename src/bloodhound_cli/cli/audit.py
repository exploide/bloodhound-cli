import sys

import click
from cymple import QueryBuilder

from bloodhound_cli.api.from_config import api
from bloodhound_cli.constants import RID
from bloodhound_cli.logger import log


@click.command()
@click.option("--domain", "-d", metavar="DOMAIN", help="Audit specific domain only.")
def audit(domain):
    """Audit domains for potential security issues."""

    domains = sorted((d["name"], d["id"]) for d in api.domains())
    if domain:
        domains = [d for d in domains if d[0] == domain.upper()]
        if not domains:
            log.error("Unknown domain %s.", domain)
            sys.exit(1)

    for dom, domsid in domains:
        print(dom)
        print("=" * len(dom))
        print()

        print("[*] Kerberoastable user accounts of high value (enabled)")
        result = api.users(domainsid=domsid, hasspn=True, enabled=True)
        result = [n for n in result if "admin_tier_0" in n["properties"].get("system_tags", "")]
        count = len(result)
        print(f"    {count} accounts found")
        result = sorted(n["properties"]["name"] for n in result)
        for n in result:
            print(n)
        print()

        print("[*] AS-REP-roastable user accounts (enabled)")
        result = api.users(domainsid=domsid, dontreqpreauth=True, enabled=True)
        count = len(result)
        print(f"    {count} accounts found")
        result = sorted(n["properties"]["name"] for n in result)
        for n in result:
            print(n)
        print()

        print("[*] Accounts trusted for unconstrained delegation (enabled, no DCs)")
        query = QueryBuilder().match().node(ref_name="dc") \
            .related_to("MemberOf", min_hops=1, max_hops=-1) \
            .node(labels="Group", ref_name="g") \
            .where("g.objectid", "=", f"{domsid}-{RID.DOMAIN_CONTROLLERS}") \
            .cypher("WITH COLLECT(dc) AS exclude") \
            .match().node(ref_name="n") \
            .where_multiple({
                "n.domainsid": domsid,
                "n.unconstraineddelegation": True,
                "n.enabled": True,
            }) \
            .cypher("AND NOT n IN exclude") \
            .return_literal("n")
        result = api.cypher(str(query))["nodes"].values()
        count = len(result)
        print(f"    {count} accounts found")
        result = sorted(n["properties"]["name"] for n in result)
        for n in result:
            print(n)
        print()

        print()
