# Copyright (C) 2015-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from unittest.mock import patch


@patch('swh.loader.tar.loader.RemoteTarLoader.load')
def test_tar_loader_task(mock_loader, swh_app, celery_session_worker):
    mock_loader.return_value = {'status': 'eventful'}

    res = swh_app.send_task(
        'swh.loader.tar.tasks.LoadTarRepository',
        ('origin', 'visit_date', 'last_modified'))
    assert res
    res.wait()
    assert res.successful()

    # given
    actual_result = res.result

    assert actual_result == {'status': 'eventful'}

    mock_loader.assert_called_once_with(
        origin='origin', visit_date='visit_date',
        last_modified='last_modified')
