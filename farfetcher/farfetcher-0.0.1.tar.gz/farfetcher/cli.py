
import click

from tqdm import tqdm
from farfetcher import Farfetcher

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    pass


@cli.command("crawl")
@click.option("--num-pages", "-p", default=180, help="No. of pages to crawl.")
def crawl_listings(num_pages):
    ff = Farfetcher()
    all_response_jsons = []
    for i in range(1,num_pages+1):
        all_response_jsons.append(ff.listings(page=i)
