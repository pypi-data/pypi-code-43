import subprocess

import click


@click.command()
@click.argument("url")
@click.option("-s", "--save-path", default="urls.txt", show_default=True)
def cli(url, save_path):
    assert url.startswith("http")

    p = subprocess.run(
        ["youtube-dl", "--get-id", "--no-warnings", url],
        capture_output=True,
        check=True,
    )
    video_ids = p.stdout.decode("utf-8").split()
    urls = [f"https://www.youtube.com/watch?v={vid}\n" for vid in video_ids]
    with open(save_path, "w") as f:
        f.writelines(urls)


if __name__ == "__main__":
    cli()
