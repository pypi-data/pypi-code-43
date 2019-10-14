import os
import logging
import hashlib
import platform
import shutil
from datetime import datetime
from PIL import Image
import piexif


class FileObj(object):
    """Abstraction around an arbitrary disk-based file

    This interface provides common functions used by our image processing
    scripts for interacting with files of various types, typically containing
    raster image data
    """

    # EXIF metadata field containing description of the model of the device used
    # to capture the image data contained therein
    _MODEL_KEY = 272

    def __init__(self, path):
        """
        Args:
            path (str): path to the file to manage
        """
        assert os.path.exists(path)
        self._log = logging.getLogger(__name__)
        self._path = path
        self._checksum = None
        self._creation_date = None

    @staticmethod
    def _calc_checksum(file_name):
        """Calculates the checksum of a file

        Args:
            file_name(str):
                path to file to analyse

        Returns:
            str:
                sha512 hash of the file
        """
        retval = hashlib.sha512()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                retval.update(chunk)
        return retval.hexdigest()

    @staticmethod
    def _calc_creation_date(path):
        """Gets the creation date for a file

        NOTE:
            Deducing the file creation date is platform specific so this helper
            method hides those complexities and provides a more Pythonic
            data structure describing the creation date to the caller

        Args:
            path (str):
                path to the file to analyse

        Returns:
            datetime.datetime:
                Creation date for the file
        """
        if platform.system() == 'Windows':
            return datetime.fromtimestamp(os.path.getctime(path))

        stat = os.stat(path)
        if platform.system() == "Darwin":
            return datetime.fromtimestamp(stat.st_birthtime)

        return datetime.fromtimestamp(stat.st_mtime)

    @property
    def checksum(self):
        """str: sha checksum of the file"""
        if self._checksum is None:
            self._checksum = FileObj._calc_checksum(self._path)
        return self._checksum

    @property
    def path(self):
        """str: absolute path to the file managed by this object"""
        return os.path.abspath(self._path)

    @property
    def filename(self):
        """str: the file name without preceding path characters"""
        return os.path.split(self.path)[-1]

    @property
    def creation_date(self):
        """datetime.datetime: date the file was created"""
        if self._creation_date is None:
            self._creation_date = FileObj._calc_creation_date(self._path)
        return self._creation_date

    @property
    def is_image(self):
        """bool: checks to see if this file is a known image file format"""
        try:
            # Attempt to parse the source file using our image library
            img = Image.open(self._path)

            # If we get here we assume the file was successfully parsed by
            # our image library and thus must be an image file, so just close
            # the file handle and return
            img.close()
            return True
        except IOError:
            # If we can't parse it, assume this is a non-image file
            # and just skip it
            return False

    def copy_to(self, target_dir):
        """Copies this file to a secondary location

        NOTE:
            This FileObj instance will still point to the original file as it
            existed before the copy.

        Args:
            target_dir (str): path to the folder to copy the file to

        Returns:
            FileObj: reference to a new file object describing the copied file
        """
        target_file = os.path.join(target_dir, self.filename)
        shutil.copy2(self._path, target_dir)
        return FileObj(target_file)

    def move_to(self, target_dir):
        """Moves this file to a secondary location

        This can be faster for large files that are stored on the same disk
        or file system since the data can remain at rest and simply the file
        allocation table gets updated

        NOTE:
            This FileObj instance will still point to the original file as it
            existed before the move, therefore calling this method effectively
            invalidates this instance of the class. No further operations
            should be made against this instance after calling this method.

        Args:
            target_dir (str): path to the folder to move the file to

        Returns:
            FileObj: reference to a new file object describing the moved file
        """
        target_file = os.path.join(target_dir, self.filename)
        shutil.move(self._path, target_file)
        return FileObj(target_file)

    def delete(self):
        """deletes this file from disk

        NOTE:
            This FileObj instance will still point to the original file as it
            existed before the deletion, therefore calling this method
            effectively invalidates this instance of the class. No further
            operations should be made against this instance after calling
            this method.
        """
        os.remove(self._path)

    def convert_progressive(self):
        """Helper method that converts a progressive encoded JPEG to a non-
        progressive format"""
        temp_suffix = ".new"
        temp_filename = self._path + temp_suffix

        # Parse our image file
        with Image.open(self._path) as img:

            # Check the EXIF data to see if it "looks" to be progressive format
            xf = img.getexif()
            if xf[FileObj._MODEL_KEY] != "Moto X Play":
                return

            # Before we try and convert our progressive format file, make sure
            # our temporary output file doesn't already exist
            if os.path.exists(temp_filename):
                raise Exception(
                    f"Can not convert image file {self._path} to "
                    f"non-progressive format. Temporary file {temp_filename} "
                    f"already exists."
                )

            # Convert our original file to the new format
            exif_dict = piexif.load(img.info["exif"])
            exif_data = piexif.dump(exif_dict)

            self._log.info(
                f"Converting file {self._path} from progressive "
                f"format to non-progressive"
            )
            img.save(
                temp_filename,
                "JPEG",
                quality=90,
                optimize=True,
                progressive=False,
                exif=exif_data
            )

        # After the conversion process is complete we swizzle the source files,
        # removing the original file and renaming the temporary file to match
        # the original source file
        os.remove(self._path)
        os.rename(temp_filename, temp_filename.rstrip(temp_suffix))
