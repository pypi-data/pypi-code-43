import json
import logging
import sys

import click

import antares_client
from antares_client.search import JobStatus

logger = logging.getLogger("cli")
logger.setLevel(logging.DEBUG)


def search_progress_callback(status, **kwargs):
    if status == JobStatus.SUBMITTED:
        logger.info("Job {id} - Submitted to ANTARES server".format(**kwargs["job"]))
        logger.info("Job {id} - Status URL: {urls[status]}".format(**kwargs["job"]))

    elif status == JobStatus.PROCESSING:
        logger.info(
            "Job {id} - ANTARES server processed {recordsProcessed} / {recordsTotal} records".format(
                **kwargs["job"]
            )
        )

    elif status == JobStatus.READY:
        logger.info("Job {id} - ANTARES finished processing".format(**kwargs["job"]))
        logger.info("Job {id} - Download URL: {urls[download]}".format(**kwargs["job"]))

    elif status == JobStatus.DOWNLOADING:
        logger.info(
            "Job {id} - Downloading results from ANTARES server".format(**kwargs["job"])
        )

    elif status == JobStatus.COMPLETED_DOWNLOADING:
        logger.info("Job {id} - Completed download".format(**kwargs["job"]))

    elif status == JobStatus.ERRORED:
        logger.error("Job {id} - Fatal error".format(**kwargs["job"]))


@click.command()
@click.option(
    "--output-format",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Format of output file (one of: ``{'json', 'csv'}``, default, ``'json'``)",
)
@click.option(
    "--decompress/--compress",
    default=False,
    help="Decompress or compress (gzip) the results before writing to file (default, ``compress``)",
)
@click.option(
    "-o",
    "--output",
    type=click.File("wb"),
    default="-",
    help="Location to write output file (default, ``STDOUT``)",
)
@click.argument("query-file", type=click.File("rb"))
def search(query_file, output, decompress, output_format):
    """
    Download an ElasticSearch query result set from ANTARES.

    If you have a file ``query.json`` with an ElasticSearch query, e.g.::

    \b
    {
      "query": {
        "range": {
          "locus_id": {
            "gte": 100,
            "lte": 20000
          }
        }
      }
    }

    Then the command:

    ``antares search -o output.json query.json``

    Will download the results of the search query to ``output.json``.

    These commands play nicely with Unix standard streams so this is
    equivalent:

    ``cat query.json | antares-client search -o output.json -``

    To write the results to STDOUT, do not pass anything for the
    ``-o/--output`` option:

    ``cat query.json | antares-client search -``

    """
    query = json.loads(query_file.read().decode("utf-8"))
    logger.info("Submitting query to ANTARES server: {}".format(query))
    try:
        result_set = antares_client.search._raw_search(  # pylint: disable=protected-access
            query,
            output_format=output_format,
            decompress=decompress,
            progress_callback=search_progress_callback,
        )
        output.write(result_set)
    except:  # pylint: disable=bare-except
        logger.exception("Encountered a fatal error:")
        sys.exit(1)
