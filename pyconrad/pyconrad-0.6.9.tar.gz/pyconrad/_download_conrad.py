import os.path
import zipfile
from os.path import join

__conrad_url = "https://www5.cs.fau.de/fileadmin/user_upload/CONRAD_1.1.0.zip"
__conrad_release = __conrad_url.split('/')[-1].rstrip(".zip")
__conrad_jar = __conrad_release.lower() + ".jar"
__conrad_download_dir = os.path.dirname(__file__)

__linux_jocl = "https://search.maven.org/remotecontent?filepath=org/jogamp/jocl/jocl/2.3.2/jocl-2.3.2-natives-linux-amd64.jar"  # noqa
__jogl_all = "https://repo1.maven.org/maven2/org/jogamp/jogl/jogl-all-main/2.3.2/jogl-all-main-2.3.2.jar"
__ij_url = "http://rsb.info.nih.gov/ij/ij.jar"


def conrad_jar_filename():
    return __conrad_jar


def conrad_jar_dir():
    return os.path.join(__conrad_download_dir, __conrad_release.replace('_', ' '))


def conrad_jar_file():
    return os.path.join(conrad_jar_dir(), __conrad_jar)


def download_file(url, download_dir):
    import sys
    file_name = url.split('/')[-1]

    if sys.version_info[0] == 3:
        from urllib.request import urlopen
    else:
        from urllib import urlopen
    u = urlopen(url)
    with open(join(download_dir, file_name), 'wb') as f:
        file_size_dl = 0
        block_sz = 8192
        print("Downloading %s..." % file_name)
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)


def download_conrad(dest_dir=__conrad_download_dir):
    import os

    __conrad_download_dir = dest_dir

    file_name = __conrad_url.split('/')[-1]
    zip_path = os.path.join(__conrad_download_dir, __conrad_url.split('/')[-1])

    download_file(__conrad_url, __conrad_download_dir)

    print("Extracting %s..." % file_name)
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(__conrad_download_dir)
    zip_ref.close()
    os.remove(zip_path)
    print("Finished extracting.")

    try:
        from sys import platform
        if platform == "linux" or platform == "linux2":
            download_file(__linux_jocl, conrad_jar_dir())
    except Exception as e:
        print(e)

    try:
        download_file(__jogl_all, conrad_jar_dir())
    except Exception as e:
        print(e)
    try:
        download_file(__ij_url, conrad_jar_dir())
    except Exception as e:
        print(e)
