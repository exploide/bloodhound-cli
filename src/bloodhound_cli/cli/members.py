import sys

import click

from bloodhound_cli.api.from_config import api
from bloodhound_cli.logger import log


@click.command()
@click.argument("group")
@click.option("--indirect", "-i", is_flag=True, help="Include indirect members and hide groups in output.")
@click.option("--enabled/--disabled", default=None, help="Show only enabled/disabled members.")
@click.option("--sam", is_flag=True, help="Show SAM account name.")
@click.option("--sep", "-s", metavar="SEP", default="\t", help="Separator between fields (default: tab).")
def members(indirect, group, enabled, sam, sep):
    """Get lists of group members.

    The full BloodHound label must be given as the group name.
    """

    group_search = api.search(group, kind="Group")
    group_search = [x for x in group_search if x["name"].upper() == group.upper()]
    if len(group_search) < 1:
        log.error("No group found with name: %s", group)
        sys.exit(1)
    group_sid = group_search[0]["objectid"]

    result = api.group_members(group_sid, indirect_members=indirect)
    result = sorted(result, key=lambda m: (m["properties"].get("domain", "").upper(), (m["properties"].get("name", ""))))

    for member in result:
        if indirect and member["kind"] == "Group":
            continue
        props = member["properties"]
        if enabled is not None and enabled != props.get("enabled"):
            continue
        try:
            out = [props["name"]]
        except KeyError:
            continue
        if sam:
            try:
                out.append(props["samaccountname"])
            except KeyError:
                out.append("")
        print(sep.join(out))
