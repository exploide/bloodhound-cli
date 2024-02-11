import click

from bloodhound_cli.__about__ import __version__
from bloodhound_cli import logger
from .auth import auth
from .domains import domains


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--debug", is_flag=True, help="Enable debug output.")
@click.version_option(version=__version__, prog_name="bhcli")
def bloodhound_cli(debug=False):
    """CLI tool to interact with the BloodHound CE API"""

    logger.set_loglevel(debug)


bloodhound_cli.add_command(auth)
bloodhound_cli.add_command(domains)
