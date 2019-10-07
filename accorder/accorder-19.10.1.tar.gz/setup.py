from setuptools import setup

setup(
    name="accorder",
    version="19.10.01",
    author="Marcell Mars",
    author_email="ki.ber@kom.uni.st",
    home_page="https://www.memoryoftheworld.org",
    description="Accorder makes Calibre library portable as standalone webapp and ready to be shared at Memory of the World Library.",
    long_description="Accorder takes care of various tasks which Memory of the World amateur librarians do in order to maintain their shared catalogs online. It builds searchable, standalone, portable webapp which one could then just copy to USB disk and open BROWSE_LIBRARY.html in her web browser. It uploads all of the books and metadata from local Calibre's library (together with portable webapp) to the server. It helps a librarian to maintain and share her catalog at https://library.memoryoftheworld.org together with other amateur librarians. It does all of above in one go by typing: accorder release PROFILE. The configuration file will keep information about one or more PROFILE. Under every PROFILE's configuration section there will be information about the directory path of local Calibre's library, librarian's name, credentials needed to upload the files to the destination server etc.",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3 :: Only",
        "Environment :: Console",
        "Topic :: Communications :: File Sharing",
    ],
    python_requires='>=3.6',
    py_modules=["accorder"],
    packages=["accorder", "accorder.utils", "accorder.assets"],
    install_requires=["Click", "dataclasses", "setuptools"],
    entry_points={"console_scripts": ["accorder = accorder:cli"]},
    include_package_data=True
)
