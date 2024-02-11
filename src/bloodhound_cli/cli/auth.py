import click

from bloodhound_cli.api import Api
from bloodhound_cli.config import config
from bloodhound_cli.logger import log


@click.command()
@click.argument("url")
@click.option("--username", "-u", metavar="USERNAME", prompt=True, help="Username for login.")
@click.option("--password", "-p", metavar="PASSWORD", prompt=True, hide_input=True, help="Password for login.")
def auth(url, username, password):
    """Authenticate to the server and configure an API token.

    The argument URL is the base URL of the BloodHound API server.
    Username and password will be prompted for when not specified.
    """

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    log.info("Authenticating to the BloodHound server...")
    api = Api(url)
    result = api.login(username, password)

    log.info("Creating new API token...")
    token_name = f"bhcli_{username}"
    api = Api(url, bearer=result["session_token"])
    result = api.create_token(token_name, result["user_id"])

    log.info("Storing API token to config file: %s", config.config_file)
    config.update(url=url, token_id=result["id"], token_key=result["key"])
    log.info("bhcli is now configured and ready to access the API.")
