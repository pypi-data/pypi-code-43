import glob
import os
import subprocess
import time

import click


class Downloader(object):
    def __init__(self, batch_file):
        self.batch_file = batch_file

    def batch_download(self):
        with open(self.batch_file) as f:
            urls = f.read().split()
        for url in urls:
            if url == '' or url.startswith('#'):
                continue
            self.download_video(url)
            self.update_batch_file(url)

    def download_video(self, url):
        click.echo(click.style(f'Start downloading {url}', fg='green'))
        for retry in range(10):
            try:
                p = subprocess.run(["youtube-dl", url], check=True)
                break
            except:
                time.sleep(10*retry)

    def update_batch_file(self, finished_url):
        with open(self.batch_file) as f:
            urls = f.read().split()
        with open(self.batch_file, 'w') as f:
            for url in urls:
                if url == finished_url:
                    url = '#' + url
                f.write(url)
                f.write('\n')


@click.command()
@click.option('-a', '--batch-file')
@click.option('-u', '--url',)
def cli(batch_file, url):
    dl = Downloader(batch_file)
    if url is not None:
        assert url.startswith('http')
        dl.download_video(url)
    else:
        dl.batch_download()


if __name__ == '__main__':
    cli()
