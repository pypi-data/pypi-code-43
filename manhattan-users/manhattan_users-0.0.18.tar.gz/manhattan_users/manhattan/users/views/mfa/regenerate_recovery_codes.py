"""
Regenerate the user's list of recovery codes.
"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.manage.views import factories
from manhattan.secure import random_code

__all__ = ['regenerate_recovery_codes_chains']


# Define the chains
regenerate_recovery_codes_chains = ChainMgr()

# POST
regenerate_recovery_codes_chains['post'] = Chain([
    'config',
    'authenticate',
    'regenerate_recovery_codes',
    'redirect'
])

regenerate_recovery_codes_chains.set_link(factories.config())
regenerate_recovery_codes_chains.set_link(factories.authenticate())
regenerate_recovery_codes_chains.set_link(
    factories.redirect('mfa_recovery_codes')
)

@regenerate_recovery_codes_chains.link
def regenerate_recovery_codes(state):
    user_cls = state.manage_config.frame_cls
    prefix = user_cls.get_settings_prefix()

    # Generate the new recovery codes
    recovery_codes = []
    recovery_code_count = flask\
        .current_app\
        .config[f'{prefix}_MFA_RECOVERY_CODES']

    for i in range(0, recovery_code_count):
        recovery_codes.append(
            random_code(
                flask.current_app.config[f'{prefix}_MFA_RECOVERY_CODE_LENGTH']
            )
        )

    # Save the new recovery codes
    state.manage_user.logged_update(
        state.manage_user,
        {'mfa_recovery_codes': recovery_codes},
        'mfa_recovery_codes',
        'modified'
    )

    # Notify the user that the recovery codes have been regenerated
    flask.flash('New recovery codes generated')
