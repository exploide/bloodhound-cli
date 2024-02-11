import sys

from bloodhound_cli.api.exceptions import ApiException
from bloodhound_cli.cli import bloodhound_cli
from bloodhound_cli.logger import log


def main():
    try:
        sys.exit(bloodhound_cli())
    except ApiException as e:
        log.error("%s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
