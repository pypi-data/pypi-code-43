import json
import click
from dataclasses import dataclass
from accorder.utils.motw_client import add_library
from accorder.utils.motw_client import bookids
from accorder.utils.motw_client import remove_books
from accorder.utils.motw_client import library_on
from accorder.utils.motw_client import library_off
from accorder.utils.motw_client import upload_books
from accorder.utils.motw_client import load_books
from accorder.utils.configs import edit_config
from accorder.utils.configs import check_profile


@dataclass(init=False)
class Submit:
    submit_off: bool = False
    submit_domain: str
    submit_subdomain: str
    submit_api: str
    submit_upload_api: str
    submit_librarian: str
    submit_library_uuid: str
    submit_library_secret: str
    submit_data_js: str

    def submit(self):
        lsb_url = f"//{self.submit_subdomain}.{self.submit_domain}/"
        click.echo(f">>>  {self.submit_librarian} at https:{lsb_url}")

        try:
            add = add_library(
                self.submit_api, self.submit_library_uuid, self.submit_library_secret
            )
            if add[0] == 200:
                click.echo(
                    f"{self.submit_librarian} from {lsb_url} added to {self.submit_api}"
                )
            elif add[0] == 202:
                # click.echo(add[1].decode())
                pass
        except Exception as e:
            click.echo(f"add_library failed: {e}")

        if self.submit_off:
            lib_res = library_off(
                self.submit_api, self.submit_library_uuid, self.submit_library_secret
            )
            if lib_res[0] == 200:
                click.echo(
                    f"{self.submit_librarian}'s library at {self.submit_api} is now OFF."
                )
            elif lib_res[0] == 202:
                click.echo(
                    f"{self.submit_librarian}'s library at {self.submit_api} has already been OFF. Don't flog a dead horse!"
                )
            click.get_current_context().exit()

        bids = bookids(
            self.submit_api, self.submit_library_uuid, self.submit_library_secret
        )
        if bids[0] == 200:
            bids = json.loads(bids[1].decode())
        else:
            raise Exception(
                f"Request to {self.submit_api} for book ids of {self.submit_library_uuid} failed."
            )
        # books_list = calibre_to_json(library_uuid, library_secret, librarian, db_path)
        books_list = []
        for i in range(1, 9):
            with open(f"{self.submit_data_js}data{i}.js") as f:
                f.seek(15)
                books_list += json.loads(f.read())["books"]
        rids = set(
            [
                s.split("___")[0]
                for s in list(
                    set(bids)
                    - set(
                        [
                            "{}___{}".format(b["_id"], b["last_modified"])
                            for b in books_list
                        ]
                    )
                )
            ]
        )
        if len(rids) > 0:
            click.echo(f"{len(rids)} books changed or deleted.")
        else:
            click.echo("No books changed or deleted.")
        if rids:
            reset = remove_books(
                self.submit_api,
                self.submit_library_uuid,
                self.submit_library_secret,
                json.dumps(list(rids)),
                True,
            )
            if reset[0] == 200:
                reset = json.loads(reset[1].decode())
            else:
                raise Exception(
                    f"Request to {self.submit_api} to remove books from {self.submit_library_uuid} failed."
                )

            if reset["reset"]:
                # library_off(library_uuid, library_secret)
                lib_res = library_on(
                    self.submit_api,
                    self.submit_library_uuid,
                    self.submit_library_secret,
                    self.submit_librarian,
                    lsb_url,
                    "on",
                )
                if lib_res[0] == 200:
                    click.echo(
                        f"{self.submit_librarian}'s {len(rids)} books updated or deleted from {self.submit_api}"
                    )
            else:
                lib_res = library_on(
                    self.submit_api,
                    self.submit_library_uuid,
                    self.submit_library_secret,
                    self.submit_librarian,
                    lsb_url,
                )
                if lib_res[0] == 202:
                    click.echo(
                        f"{self.submit_librarian}'s {len(rids)} books updated or deleted from {self.submit_api}"
                    )

        bids = bookids(
            self.submit_api, self.submit_library_uuid, self.submit_library_secret
        )
        if bids[0] == 200:
            bids = json.loads(bids[1].decode())
        else:
            raise Exception(
                f"Request to {self.submit_api} for book ids of {self.submit_library_uuid} failed."
            )
        sids = set(
            [
                s.split("___")[0]
                for s in list(
                    set(
                        [
                            "{}___{}".format(b["_id"], b["last_modified"])
                            for b in books_list
                        ]
                    )
                    - set(bids)
                )
            ]
        )

        if len(sids) > 0:
            click.echo(f"{len(sids)} books to upload... ", nl=False)
        else:
            click.echo("No books to upload.")

        if len(sids) == 0 and len(rids) == 0:
            lib_res = library_on(
                self.submit_api,
                self.submit_library_uuid,
                self.submit_library_secret,
            )

            if lib_res[0] == 200:
                click.echo(f"{self.submit_librarian}'s library was OFF. Now it's back online. YAY!")

        if sids:
            # reset = add_books(
            upload = upload_books(
                self.submit_upload_api,
                self.submit_library_uuid,
                self.submit_library_secret,
                json.dumps([b for b in books_list if b["_id"] in sids]),
                True,
            )
            if upload[0] == 200:
                reset = load_books(
                    self.submit_api,
                    "add",
                    self.submit_library_uuid,
                    self.submit_library_secret,
                )
            if reset[0] == 200:
                reset = json.loads(reset[1].decode())
                click.echo("Uploaded.")
            else:
                raise Exception(
                    f"Request to load books of just uploaded {self.submit_library_uuid} failed."
                )

            if reset["reset"]:
                # library_off(library_uuid, library_secret)
                lib_res = library_on(
                    self.submit_api,
                    self.submit_library_uuid,
                    self.submit_library_secret,
                    self.submit_librarian,
                    lsb_url,
                    "on",
                )
                if lib_res[0] == 200:
                    click.echo(
                        f"{self.submit_librarian}'s {len(sids)} books added to {self.submit_api}."
                    )
            else:
                lib_res = library_on(
                    self.submit_api,
                    self.submit_library_uuid,
                    self.submit_library_secret,
                    self.submit_librarian,
                    lsb_url,
                )
                if lib_res[0] == 200:
                    click.echo(
                        f"{self.submit_librarian}'s {len(sids)} books added to {self.submit_api}."
                    )

        click.echo("")


def run_submit(app_name, profile, librarian, off):
    config = edit_config(app_name, profile, librarian)
    check_profile(config, profile)

    r = Submit()
    if off:
        r.submit_off = off
    r.submit_api = config[profile]["motw"]["api"]
    r.submit_upload_api = config[profile]["motw"]["upload_api"]
    r.submit_subdomain = config[profile]["motw"]["subdomain"]
    r.submit_domain = config[profile]["motw"]["domain"]
    r.submit_librarian = config[profile]["calibre"]["librarian"]
    r.submit_library_uuid = config[profile]["calibre"]["library_uuid"]
    r.submit_library_secret = config[profile]["calibre"]["library_secret"]
    r.submit_data_js = f'{config[profile]["calibre"]["local_directory"]}/static/'

    click.echo(f">>>> SUBMIT METADATA TO {r.submit_api}")
    r.submit()
