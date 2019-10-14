#!/usr/bin/env python
import click
import os
import logging
from friendlypics.file_object import FileObj
from friendlypics.manifest_file import ManifestFile


MANIFEST_FILENAME = ".friendlypics.manifest"
LOG_FILENAME = "fpics.log"


def configure_logger():
    """Configures the default logging subsystem for the tool"""
    global_log = logging.getLogger()

    # Log all log data to a file
    fh = logging.FileHandler(LOG_FILENAME, "w")
    fh.setLevel(logging.DEBUG)
    format_str = "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
    file_formatter = logging.Formatter(format_str)
    fh.setFormatter(file_formatter)
    global_log.setLevel(logging.DEBUG)
    global_log.addHandler(fh)


@click.group("main")
@click.version_option()
def main():
    """Image manipulation utility"""
    configure_logger()


@main.command()
@click.argument("source_dir")
@click.argument("target_dir")
@click.option("--move", is_flag=True,
              help="Move images to the target folder instead of copying them")
@click.option("--overwrite", is_flag=True,
              help="Overwrite existing files in the target folder instead of "
                   "ignoring them.")
@click.option("--preprocess", is_flag=True,
              help="Convert progressive encoded images to regular format")
def sort(source_dir, target_dir, move, overwrite, preprocess):
    """Sort images from a source folder based on date"""
    log = logging.getLogger(__name__)
    root_src_dir = os.path.abspath(os.path.expanduser(source_dir))
    root_dest_dir = os.path.abspath(os.path.expanduser(target_dir))
    click.echo(f"Indexing source dir {root_src_dir}...")

    # Create a manifest file in each output folder containing
    # the names and checksums of all files in the folder
    target_manifests = dict()

    for parent, dir_names, file_names in os.walk(root_src_dir):
        click.echo(f"Scanning dir {parent}")
        for cur_file_name in file_names:
            cur_file = FileObj(os.path.join(parent, cur_file_name))

            # If our source file is not a known image file format, skip it
            if not cur_file.is_image:
                continue

            # If our target / output folder, based on the year the source
            # file was created, doesn't already exist lets create it (ie:
            # in preparation for moving / copying the file there).
            output_dir = os.path.join(
                root_dest_dir,
                str(cur_file.creation_date.year)
            )
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Get the manifest file for the target folder
            if output_dir not in target_manifests:
                target_manifests[output_dir] = ManifestFile(
                    os.path.join(output_dir, MANIFEST_FILENAME)
                )
            cur_manifest = target_manifests[output_dir]

            # See if the source file already exists in the target location
            if cur_manifest.contains(cur_file) and not overwrite:
                if move:
                    log.info(
                        f"File {cur_file.path} already exists in target folder "
                        f"{output_dir} but 'move' operation has been "
                        f"requested. Deleting original file."
                    )
                    cur_file.delete()
                else:
                    log.info(
                        f"Skipping copying file {cur_file.path} since it "
                        f"already exists in the target folder {output_dir}."
                    )
                continue

            # Once we get here we know the source file hasn't been copied
            # to the target folder yet, however there may still be a file
            # in the target folder with the same name but different content.
            target_file = os.path.join(output_dir, cur_file.filename)
            if os.path.exists(target_file):
                if not overwrite:
                    log.info(
                        f"Skipping copying of source file {cur_file.path} as a "
                        f"file with the same name but different content exists "
                        f"in the output folder {target_file}."
                    )
                    continue
                log.warning(
                    f"Overwriting existing file {target_file} with the "
                    f"source file {cur_file.path}."
                )

            # Once we get here we should be certain that the file from the
            # source folder doesn't exist anywhere in the target folder, OR
            # if it does exist in some variation we have been asked to overwrite
            # it in the target. Either way proceed with the file operation.
            if move:
                log.info(f"Moving file {cur_file.path} to {output_dir}")
                new_file = cur_file.move_to(output_dir)
            else:
                log.info(f"Copying file {cur_file.path} to {output_dir}")
                new_file = cur_file.copy_to(output_dir)

            # update our manifest file for the new entry
            cur_manifest.add_entry(new_file)

            # See if we've been asked to pre-process the image data to "fix"
            # progressive loading images (ie: so they work correctly with
            # Shutterfly)
            if not preprocess:
                continue
            new_file.convert_progressive()

    click.echo(
        f"Sorting completed successfully. See log file {LOG_FILENAME} "
        f"for details on work performed.")


if __name__ == "__main__":
    main()
