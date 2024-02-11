import json
import time
from zipfile import ZipFile

import click

from bloodhound_cli.api.from_config import api
from bloodhound_cli.logger import log


@click.command()
@click.argument("files", metavar="FILE...", nargs=-1, required=True, type=click.Path(exists=True))
def upload(files):
    """Upload and ingest files from the BloodHound collector.

    Supported are JSON and ZIP files.
    """

    log.info("Starting new file upload job...")
    upload_id = api.start_upload()["id"]

    for file in files:
        if file.lower().endswith(".json"):
            log.info("Uploading file %s", file)
            with open(file, "r", encoding="utf-8-sig") as f:
                content = json.load(f)
            api.upload_file(upload_id, content)

        elif file.lower().endswith(".zip"):
            log.info("Processing ZIP file %s", file)
            with ZipFile(file) as z:
                for zipped_file in z.namelist():
                    if zipped_file.lower().endswith(".json"):
                        log.info("Uploading file %s from %s", zipped_file, file)
                        with z.open(zipped_file) as f:
                            content = json.load(f)
                        api.upload_file(upload_id, content)
                    else:
                        log.warning("ZIP %s contains unsupported file %s which will be ignored", file, zipped_file)

        else:
            log.warning("File of unsupported type will be ignored: %s", file)

    log.info("Ending file upload job...")
    api.end_upload(upload_id)

    log.info("Now waiting for ingestion being complete...")
    while True:
        time.sleep(5)
        result = api.upload_status(upload_id)
        if result[0]["status"] == 2:
            break
    log.info("Ingestion completed, the data is now available.")
