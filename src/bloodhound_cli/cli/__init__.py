import click

from bloodhound_cli.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="bhcli")
def bloodhound_cli():
    click.echo("Hello world!")
