import json
import shutil
import pkg_resources
import pathlib
import os
import click
from dataclasses import dataclass
from accorder.utils.motw_client import calibre_to_json
from accorder.utils.configs import edit_config


@dataclass(init=False)
class BuildPortable:
    buildportable_library_uuid: str
    buildportable_library_secret: str
    buildportable_librarian: str
    buildportable_local_directory: str

    def copy_resources(self, pkg_dir, root_dest):
        for f in pkg_resources.resource_listdir("accorder", pkg_dir):
            if pkg_resources.resource_isdir("accorder", f"{pkg_dir}/{f}"):
                p = pathlib.Path(
                    pkg_resources.resource_filename("accorder", f"{pkg_dir}/{f}")
                )
                rel_path = pathlib.PurePath(*p.parts[p.parts.index("assets") + 1 :])
                dest_path = pathlib.PurePath(root_dest, rel_path)
                os.makedirs(str(dest_path), exist_ok=True)
                self.copy_resources(f"{pkg_dir}/{f}", root_dest)
            else:
                p = pathlib.Path(
                    pkg_resources.resource_filename("accorder", f"{pkg_dir}/{f}")
                )
                rel_path = str(pathlib.PurePath(*p.parts[p.parts.index("assets") + 1 :]))
                shutil.copy2(str(p), f"{root_dest}{rel_path}")

    def run_buildportable(self):
        books = calibre_to_json(
            self.buildportable_library_uuid,
            self.buildportable_library_secret,
            self.buildportable_librarian,
            f"{self.buildportable_local_directory}metadata.db",
        )

        shutil.rmtree(
            f"{self.buildportable_local_directory}static/", ignore_errors=True
        )

        self.copy_resources("assets", self.buildportable_local_directory)

        # write first 48 books
        count = 1
        block = 24
        with open(f"{self.buildportable_local_directory}static/data{count}.js", "wb") as f:
            books_json = json.dumps({"portable": True, "total": len(books), "books": books[:block]})
            output = f"CALIBRE_BOOKS{count}={books_json}"
            f.write(output.encode())

        # write six more (2x96, 4x2304)
        count += 1
        for i in range(1, 3):
            for ii in range(2**i):
                end_block = block + 24**i*4
                with open(f"{self.buildportable_local_directory}static/data{count}.js", "wb") as f:
                    books_json = json.dumps({"portable": True, "books": books[block:end_block]})
                    output = f"CALIBRE_BOOKS{count}={books_json}"
                    f.write(output.encode())
                block = end_block

                count += 1
        # write last one with the rest
        with open(f"{self.buildportable_local_directory}static/data{count}.js", "wb") as f:
            books_json = json.dumps({"portable": True, "books": books[block:]})
            output = f"CALIBRE_BOOKS{count}={books_json}"
            f.write(output.encode())

        click.echo(
            f"\r{self.buildportable_librarian}'s portable catalog of {len(books)} books built."
        )
        click.echo(
            f"Check the webapp by opening in your browser:\n{self.buildportable_local_directory}BROWSE_LIBRARY.html"
        )
        click.echo("")


def run_build(app_name, profile, directory, librarian):
    config = edit_config(app_name, profile, directory=directory, librarian=librarian)

    r = BuildPortable()
    r.buildportable_library_uuid = config[profile]["calibre"]["library_uuid"]
    r.buildportable_library_secret = config[profile]["calibre"]["library_secret"]
    r.buildportable_librarian = config[profile]["calibre"]["librarian"]
    r.buildportable_local_directory = config[profile]["calibre"]["local_directory"]

    click.echo(">>>> BUILD PORTABLE CATALOG AS WEBAPP TO:")
    click.echo(f">>>> {r.buildportable_local_directory}")
    click.echo(f"\rbuilding {r.buildportable_librarian}'s portable.", nl=False)
    r.run_buildportable()
