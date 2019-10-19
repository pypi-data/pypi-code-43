import fs
import fs.path
from fs.opener.parse import parse_fs_url
import importlib
from functools import partial

import logging
log = logging.getLogger()

class Filepath:
    """ wraps pyfilesystem fs_url

        why needed:

        * simpler and more consistent to process all urls in same way without having to consider the filesystem
        * one step filepath methods e.g. exists, isdir
        * additional filepath methods e.g. load, save
        * differentiate filepath from string as a parameter
    """
    def __init__(self, url):
        """
        split url using | (extension to fs_url spec) or based on content

        * osfs:// (default)
        * ftp://username:password@ipaddress:port
        * s3://bucket
        * osfs://c (for windows to include drive)
        """
        # make default filesystem explicit
        if "://" not in url:
            url = f"osfs://{url}"

        # explicitly split filesystem/path
        if "|" in url:
            self.fs, self.path = url.split("|")
            return

        # parse url
        parsed = parse_fs_url(url)

        # protocol and creds
        protocol  = parsed.protocol.lower()
        if parsed.username:
            self.fs = f"{protocol}://{parsed.username}:{parsed.password}@"
        else:
            self.fs = f"{protocol}://"

        # standardise path format
        path = parsed.resource.lstrip("/")
        path = path.replace("\\", "/")
        path = fs.path.normpath(path)

        # split resource path and other components. parsed.path is currently blank in pyfilesystem after parsing.
        path = path.split("/")

        # ftp include address
        if protocol=="ftp":
            address = path.pop(0)
            self.fs = f"{self.fs}{address}"

        # s3 include bucket
        if protocol=="s3":
            bucket = path.pop(0)
            self.fs = f"{self.fs}{bucket}"

        # windows include drive
        elif protocol=="osfs":
            if path[0].endswith(":"):
                drive = path.pop(0)
                self.fs = f"{self.fs}{drive}"

        self.path = "/".join(path)

    def __getstate__(self):
        """ required for pickle """
        return self.__dict__

    def __setstate__(self, d):
        """ required for pickle """
        self.__dict__= d

    @property
    def ofs(self):
        """ return open filesystem """
        # must be here rather than __init__ as cannot be pickled
        return fs.open_fs(self.fs)

    @property
    def url(self):
        return f"{self.fs}/{self.path}"

    @property
    def name(self):
        """ return just the variable name for simple display """
        filename = fs.path.basename(self.path)
        return fs.path.splitext(filename)[0]

    def __repr__(self):
        """ unique and standardised url """
        return self.url

    def __str__(self):
        """ short name for display """
        return self.name

    def __hash__(self):
        """ unique key for dict """
        return hash(repr(self))

    def __eq__(self, other):
        return repr(self)==repr(other)

    def __getattr__(self, method):
        """ shortcut to ofs.method(path, *args, **kwargs) """
        return partial(getattr(self.ofs, method), self.path)

    def load(self):
        """ return file contents. use extension to determine driver """
        ext = fs.path.splitext(self.path)[-1] or ".pkl"
        try:
            i = importlib.import_module(f"pipemaker.filesystem.filedrivers{ext}")
        except ModuleNotFoundError:
            log.error(f"No driver found for extension {ext}. You can add one in the filedrivers folder.")
            raise
        return i.load(self)

    def save(self, obj):
        """ save obj to file. use extension to determine driver
        use temporary url then rename to ensure not visible until complete
        """
        # todo replace temp folders with temp file as simpler
        saved_path = self.path
        try:
            # save file using driver selected based on extension
            ext = fs.path.splitext(self.path)[-1] or ".pkl"
            try:
                i = importlib.import_module(f"pipemaker.filesystem.filedrivers{ext}")
            except ModuleNotFoundError:
                log.error(f"No driver found for extension {ext}. You can add one in the filedrivers folder.")
                raise

            # save to temp file so file is not visible until complete.
            dirname, filename = fs.path.split(self.path)
            temp_dir = f"{dirname}/temp"
            self.ofs.makedirs(temp_dir, recreate=True)
            self.path = f"{temp_dir}/{filename}"
            i.save(self, obj)

            # move temp file to target location
            self.move(f"{saved_path}", overwrite=True)
        except Exception:
            log.exception(f"Problem saving {self.url}")
            raise
        finally:
            # restore original path
            self.path = saved_path

