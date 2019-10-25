from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import csv
import sys

import click
from lxml import etree
from litezip.main import COLLECTION_NSMAP
from nebtasks.task_extensions import neb_task, NebTask

def load(cli):
    @neb_task(cli, name='shortlink-report')
    @click.option('-t', '--timeout', type=int, default=3)
    @click.argument('csv_out', type=click.Path(resolve_path=True))
    def shortlink_report_task(csv_out, timeout):
        """output a csv report of shortlinks in content"""

        fieldnames = ['module', 'shortcode', 'redirect_url']

        def follow_or_error(url):
            try:
                return urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=timeout).geturl()
            except URLError as error:
                return f'URLError: {error.reason}'
            except HTTPError as error:
                return f'HTTPError: {error.code} - {error.reason}'
            except ValueError as error:
                return 'ValueError: Cannot interpret link - does it specify HTTP(S)?'

        def before_action():
            with open(csv_out, 'w') as dump:
                writer = csv.DictWriter(dump, fieldnames=fieldnames)
                writer.writeheader()

        def content_action(id, file, resources):
            sys.stdout.write(f'Working on {id}... ')
            sys.stdout.flush()
            with open(csv_out, 'a') as dump:
                writer = csv.DictWriter(dump, fieldnames=fieldnames)

                tree = etree.parse(file)
                links = tree.xpath('//c:link', namespaces=COLLECTION_NSMAP)
                link_urls = list(filter(
                    lambda url: '/l/' in url,
                    list(map(
                        lambda link: next(iter(link.xpath('./@url', namespaces=COLLECTION_NSMAP)), ''),
                        links))))

                redirect_urls = list(map(
                    follow_or_error,
                    link_urls))
            
                link_info = zip(link_urls, redirect_urls)
                for original, redirect in link_info:
                    writer.writerow({
                        'module': id,
                        'shortcode': original,
                        'redirect_url': redirect
                    })
            print('Done')

        return NebTask(before_action=before_action,
                       module_action=content_action,
                       collection_action=content_action)