import click

from bloodhound_cli.__about__ import __version__
from bloodhound_cli import logger
from .audit import audit
from .auth import auth
from .computers import computers
from .cypher import cypher
from .domains import domains
from .groups import groups
from .stats import stats
from .upload import upload
from .users import users


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--debug", is_flag=True, help="Enable debug output.")
@click.version_option(version=__version__, prog_name="bhcli")
def bloodhound_cli(debug=False):
    """CLI tool to interact with the BloodHound CE API"""

    logger.set_loglevel(debug)


bloodhound_cli.add_command(audit)
bloodhound_cli.add_command(auth)
bloodhound_cli.add_command(computers)
bloodhound_cli.add_command(cypher)
bloodhound_cli.add_command(domains)
bloodhound_cli.add_command(groups)
bloodhound_cli.add_command(stats)
bloodhound_cli.add_command(upload)
bloodhound_cli.add_command(users)
