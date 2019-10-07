"""
Disable multi-factor authentication (MFA) for the user.
"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.forms import BaseForm, fields, validators
from manhattan.manage.views import factories, utils
from manhattan.nav import NavItem

__all__ = ['disable_chains']


# Forms

class DisableForm(BaseForm):

    current_password = fields.PasswordField(
        'Password',
        [validators.Required()]
    )

    def validate_current_password(form, field):
        """
        The user must specify their existing password to disable multi-factor
        authentication.
        """

        if not field.data:
            return

        if not form.obj.password_eq(field.data):
            raise validators.ValidationError('Password is incorrect.')


# Chains
disable_chains = ChainMgr()

# GET
disable_chains['get'] = Chain([
    'config',
    'authenticate',
    'init_form',
    'decorate',
    'render_template'
])

# POST
disable_chains['post'] = Chain([
    'config',
    'authenticate',
    'init_form',
    'validate',
    [
        [
            'disable_mfa',
            'redirect'
        ], [
            'decorate',
            'render_template'
        ]
    ]
])

# Define the links
disable_chains.set_link(
    factories.config(
        form_cls=DisableForm,
        open_user_nav=True
    )
)
disable_chains.set_link(factories.authenticate())
disable_chains.set_link(factories.validate())
disable_chains.set_link(factories.render_template('mfa/disable.html'))
disable_chains.set_link(factories.redirect('security'))

@disable_chains.link
def decorate(state):
    state.decor = utils.base_decor(state.manage_config, 'mfa_disable')
    state.decor['title'] = 'Disable 2-factor authentication'

    state.decor['breadcrumbs'].add(
        NavItem('Security', state.manage_config.get_endpoint('security'))
    )
    state.decor['breadcrumbs'].add(
        NavItem('Disable 2-factor authentication', '')
    )

@disable_chains.link
def init_form(state):
    user_cls = state.manage_config.frame_cls

    # Initialize the form
    state.form = state.form_cls(
        flask.request.form,
        obj=getattr(flask.g, user_cls.get_g_key())
    )

    # Store the user class against the form
    state.form._user_cls = user_cls

@disable_chains.link
def disable_mfa(state):
    """Disable multi-factor authentication for the user"""
    user_cls = state.manage_config.frame_cls
    user = getattr(flask.g, user_cls.get_g_key())

    # Disable MFA for the user
    user.logged_update(
        user,
        {
            'mfa_enabled': False,
            'mfa_otp_secret': None,
            'mfa_recovery_codes': None
        },
        'mfa_enabled',
        'mfa_otp_secret',
        'mfa_recovery_codes',
        'modified'
    )

    current_session = user.current_session
    current_session.mfa_authorized = None
    current_session.update('mfa_authorized')

    # Notify the user the MFA has been disabled
    flask.flash('2-factor authentication disabled')
