import json
import sys

import click

from bloodhound_cli.api.exceptions import ApiException
from bloodhound_cli.api.from_config import api
from bloodhound_cli.logger import log


@click.command()
@click.argument("file", type=click.Path(dir_okay=False))
@click.option("--save", is_flag=True, help="Save existing custom queries to file.")
def queries(file, save):
    """Import and export custom queries.

    Imports custom Cypher queries from a file to the BloodHound database.
    If --save is specified, existing queries are exported to a file instead of imported.

    For import, the file must either be in the format that --save produces or in the legacy Bloodhound's customqueries.json format.
    However, not everything from the latter might be compatible.
    """

    if save:
    # export queries
        result = api.get_saved_queries(sort_by="name")
        queries_to_export = [{key: entry[key] for key in ("name", "query", "description")} for entry in result]
        with open(file, "w", encoding="UTF-8") as f:
            json.dump(queries_to_export, f, indent=4)
        log.info("Saved %d queries to %s", len(queries_to_export), file)

    else:
    # import queries
        with open(file, "r", encoding="UTF-8") as f:
            try:
                queries_to_import = json.load(f)
            except json.decoder.JSONDecodeError:
                log.error("Cannot parse file %s. A JSON file containing custom queries is required.", file)
                sys.exit(1)

        # compatibility import of legacy BloodHound's customqueries.json
        if isinstance(queries_to_import, dict) and "queries" in queries_to_import:
            log.warning("Detected legacy BloodHound's customqueries.json format. Some queries might not be compatible with BloodHound CE.")
            compatible_queries = []
            for entry in queries_to_import["queries"]:
                if len(entry["queryList"]) > 1 or not entry["queryList"][0]["final"]:
                    log.error('Query "%s" requires node selection, which is not compatible with BloodHound CE.', entry["name"])
                    continue
                compatible_queries.append({"name": entry["name"], "query": entry["queryList"][0]["query"]})
            queries_to_import = compatible_queries

        num_queries = 0
        for query in queries_to_import:
            try:
                result = api.add_saved_query(**query)
                num_queries += 1
            except ApiException as e:
                if e.response.status_code == 400:
                    log.error('Could not import query "%s": %s', query["name"], '\n'.join(error["message"] for error in e.response.json()["errors"]))
                else:
                    raise
        log.info("Imported %d custom queries.", num_queries)
