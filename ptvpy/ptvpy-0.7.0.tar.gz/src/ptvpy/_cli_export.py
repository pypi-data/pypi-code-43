"""Subcommand `export`."""


from pathlib import Path

import click

from ._cli_utils import AddProfileDetection, CliTimer, LazyImport


scipy_io = LazyImport("scipy.io")
sqlite3 = LazyImport("sqlite3")
io = LazyImport("..io", package=__name__)


@click.command(name="export")
@click.argument("destination", type=click.Path(dir_okay=False, writable=True))
@click.option(
    "--type",
    help="Override the export type and ignore file extension if provided.",
    type=click.Choice(["csv", "xlsx", "mat", "sqlite"]),
)
@AddProfileDetection()
def export_command(**kwargs):
    """Export processed data.

    Process results can be exported to different file formats with the help of
    this subcommand. A file path specifies the DESTINATION of the exported
    data. If the export format is not specified manually (see --type) PtvPy
    tries to guess the format from the file extension in DESTINATION.
    """
    profile = kwargs["profile"]
    export_type = kwargs["type"] or Path(kwargs["destination"]).suffix[1:]
    export_type = export_type.lower()

    with CliTimer("Exporting"):
        with io.Storage(profile["general.storage_file"], "r") as file:
            data = file.load_df("particles")

        if export_type == "csv":
            data.to_csv(kwargs["destination"])

        elif export_type == "xlsx":
            try:
                data.to_excel(kwargs["destination"])
            except ImportError as error:
                if "openpyxl" in error.msg:
                    raise ImportError("'openpyxl' is needed for this export option")
                else:
                    raise

        elif export_type == "mat":
            mdict = {name: data[name].values for name in data}
            # Append "_" to column names which clash with builtin MATLAB symbols
            for name in ("size", "angle"):
                if name in mdict:
                    mdict[name + "_"] = mdict.pop(name)
            scipy_io.savemat(file_name=kwargs["destination"], mdict=mdict)

        elif export_type == "sqlite":
            with sqlite3.connect(kwargs["destination"]) as con:
                data.to_sql(name="ptvpy_particle_data", con=con)

        else:
            raise ValueError(f"export type '{export_type}' is not supported")

    click.echo(f"Exported to '{kwargs['destination']}'")
