# Copyright (C) 2015-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from celery import current_app as app

from swh.loader.tar.loader import RemoteTarLoader


@app.task(name=__name__ + '.LoadTarRepository')
def load_tar(origin, visit_date, last_modified):
    """Import a remote or local archive to Software Heritage
    """
    loader = RemoteTarLoader()
    return loader.load(
        origin=origin, visit_date=visit_date, last_modified=last_modified)
