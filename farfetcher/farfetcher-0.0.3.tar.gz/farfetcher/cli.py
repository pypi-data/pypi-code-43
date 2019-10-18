
import sys
from datetime import date

import click
from tqdm import tqdm
import pandas as pd

from farfetcher import Farfetcher

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    pass

@cli.command("crawl")
@click.option("--num-pages", "-n", default=180, help="No. of pages to crawl.")
@click.option("--output-to", "-o", default="farfetch-{}.tsv",
    help="Filename to save the dataframe."
)
def crawl_listings(num_pages, output_to):
    today = date.today()
    output_filename = output_to.format(today.isoformat())
    ff = Farfetcher()
    all_response_jsons = []
    try:
        for i in tqdm(range(1,num_pages+1)):
            all_response_jsons.append(ff.listings(page=i))
    except KeyboardInterrupt:
        pass
    df = pd.concat([pd.DataFrame.from_dict(d['products']) for d in all_response_jsons])
    df.to_csv(output_filename, sep='\t', index=False)
    print(f"TSV file saved to {output_filename}",  file=sys.stderr)
