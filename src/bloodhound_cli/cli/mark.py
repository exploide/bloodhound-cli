import sys

import click

from bloodhound_cli.api.from_config import api
from bloodhound_cli.logger import log
from .paramtypes import AssetGroupTagType


@click.command()
@click.argument("tag", type=AssetGroupTagType())
@click.argument("objects", metavar="[OBJECT]...", nargs=-1)
@click.option("--file", "-f", type=click.Path(exists=True, dir_okay=False, allow_dash=True), help="File containing object names to mark (use '-' for stdin).")
@click.option("--create-asset-group", metavar="NAME", type=str, help="Create the asset group with specified pretty name if it does not exist.")
def mark(tag, objects, file, create_asset_group):
    """Mark objects as belonging to an asset group.

    The first argument is the tag of the asset group the objects should be added to (e.g. 'owned' or 'admin_tier_0').

    The full BloodHound label must be given as the object name.
    Only User and Computer objects are supported for now.
    If the name contains an '@', it is treated as a User, otherwise as a Computer.
    """

    asset_groups = api.get_asset_groups(tag=tag)
    if len(asset_groups) == 0:
        if create_asset_group:
            log.info("Creating new asset group '%s' with tag '%s'.", create_asset_group, tag)
            api.create_asset_group(create_asset_group, tag)
            asset_groups = api.get_asset_groups(tag=tag)
        else:
            log.error("Asset group with tag '%s' not found! Use --create-asset-group to create it.", tag)
            sys.exit(1)
    asset_group_id = asset_groups[0]["id"]

    names_to_add = list(objects)

    if file:
        with click.open_file(file, mode="r", encoding="UTF-8") as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    names_to_add.append(line)

    sids_to_add = set()

    for obj in names_to_add:
        if "@" in obj:
            kind = "User"
        else:
            kind = "Computer"
        result = api.search(obj, kind)
        result = [x for x in result if x["name"].upper() == obj.upper()]
        if len(result) < 1:
            log.warning("No %s object found with name: %s", kind, obj)
            continue
        if len(result) > 1:
            log.warning("This should not happen! Found more than one %s object with name: %s", kind, obj)
            continue
        result = result[0]
        if tag in result.get("system_tags", "").split() or tag in result.get("user_tags", "").split():
            log.warning("%s object is already marked as %s: %s", kind, tag, result["name"])
            continue
        sids_to_add.add(result["objectid"])

    if sids_to_add:
        api.add_to_asset_group(asset_group_id, list(sids_to_add))
        log.info("Marked %d objects as %s.", len(sids_to_add), tag)
