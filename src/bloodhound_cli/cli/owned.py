import click

from bloodhound_cli.api.from_config import api
from bloodhound_cli.logger import log


OWNED_ASSED_GROUP_ID = 1


@click.command()
@click.argument("objects", metavar="[NAME]...", nargs=-1)
@click.option("--file", "-f", type=click.Path(exists=True), help="File containing object names to own.")
def owned(objects, file):
    """Mark objects as owned.

    The full BloodHound label must be given as the name.
    Only User and Computer objects are supported for now.
    If the name contains an '@', it is treated as a User, otherwise as a Computer.
    """

    names_to_add = list(objects)

    if file:
        with open(file, "r", encoding="UTF-8") as f:
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
        if "owned" in result["system_tags"].split():
            log.warning("%s object is already marked as owned: %s", kind, result["name"])
            continue
        sids_to_add.add(result["objectid"])

    if sids_to_add:
        api.add_to_asset_group(OWNED_ASSED_GROUP_ID, list(sids_to_add))
        log.info("Marked %d objects as owned.", len(sids_to_add))
