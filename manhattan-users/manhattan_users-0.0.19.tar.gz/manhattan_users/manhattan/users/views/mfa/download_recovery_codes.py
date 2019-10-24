"""
Download a text file containing the user's recovery codes.
"""

import io

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.manage.views import factories

__all__ = ['download_recovery_codes_chains']


# Chains
download_recovery_codes_chains = ChainMgr()

# POST
download_recovery_codes_chains['get'] = Chain([
    'config',
    'authenticate',
    'download_recovery_codes'
])

# Define the links
download_recovery_codes_chains.set_link(factories.config())
download_recovery_codes_chains.set_link(factories.authenticate())

@download_recovery_codes_chains.link
def download_recovery_codes(state):

    user_cls = state.manage_config.frame_cls
    user = getattr(flask.g, user_cls.get_g_key())

    f = io.BytesIO()
    f.write('\n'.join(user.mfa_recovery_codes).encode('utf8'))
    f.seek(0)

    return flask.send_file(
        f,
        mimetype='text/plain',
        as_attachment=True,
        attachment_filename='recovery_codes.txt'
    )
