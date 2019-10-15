from copy import copy
import os
import shutil
import sys
import urllib.parse as urlparse

SUPPORTED_PIP = "19."
SUPPORTED_POETRY = "0.12."


def run_patch(self, *args, **kwargs):
    """
    Patch function for poetry's PipInstaller.run
    """

    # create args buffer
    fixed_args = list(copy(args))

    # search for --index-url arg
    for i in range(len(args)):
        if args[i] == "--index-url" or args[i] == '-i':
            # fix creds in url
            try:
                fixed_args[i+1] = fix_creds(args[i+1])
            except Exception as e:
                sys.exit(f'Failed to fix credentials: {str(e)}')

    # call unpatched PipInstaller.run
    self._unpatched_run(*fixed_args, **kwargs)


# fix_creds
def fix_creds(url):
    """
    Encode credentials in a `url` containing unencoded credentials
    """
    # process url with urlparse
    parsed_url = urlparse.urlparse(url)

    # separate netloc into creds and host
    try:
        creds, host = parsed_url.netloc.rsplit('@', 1)
    except ValueError:
        # don't modify the url if there are no creds
        return url

    # separate creds into user and password
    user, password = creds.split(':', 1)

    # urlencode user and password
    fixed_creds = f'{urlparse.quote(user)}:{urlparse.quote(password)}'

    # reconstruct netloc with urlencoded creds
    fixed_url = parsed_url._replace(netloc=f'{fixed_creds}@{host}')

    # return fixed url
    return fixed_url.geturl()


def main():
    # add poetry dir to libdir so we can import it
    path = shutil.which("poetry")

    # exit with error if path is null
    if not path:
        sys.exit('Installation for poetry was not found')

    dirname = os.path.dirname(path)
    libdir = f'{dirname}/../lib'
    sys.path.insert(0, libdir)

    import poetry
    from poetry.installation.pip_installer import PipInstaller

    # check stuff that would disable patching
    try:
        # this will raise an exception if pip isn't installed, let poetry handle that error
        import pip

        # if pip version is not supported, raise exception
        if not pip.__version__.startswith(SUPPORTED_PIP):
            raise Exception()

        # if poetry version is not supported, raise exception
        if not poetry.__version__.startswith(SUPPORTED_POETRY):
            raise Exception()

        # save PipInstaller.run
        setattr(PipInstaller, '_unpatched_run', PipInstaller.run)

        # patch PipInstaller.run
        PipInstaller.run = run_patch

    except:
        # do nothing
        pass

    # call poetry
    poetry.console.main()


if __name__ == "__main__":
    main()
