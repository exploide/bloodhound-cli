import json

import click

from bloodhound_cli.api.from_config import api


@click.command()
@click.argument("query")
@click.option("--no-properties", "properties", flag_value=False, default=True, help="Don't return all node properties.")
def cypher(query, properties):
    """Run a raw Cypher query and print the response as JSON."""

    result = api.cypher(query, include_properties=properties)
    print(json.dumps(result, indent=4))
