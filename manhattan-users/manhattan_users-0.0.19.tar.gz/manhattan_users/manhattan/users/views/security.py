"""
Allow a user to change their password, view, enable and disable their
multi-factor authentication and
"""

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.forms import BaseForm, fields, validators
from manhattan.manage.views import factories
from manhattan.nav import Nav, NavItem
from manhattan.users.utils import apply_password_rules, password_validator
from mongoframes import Q, SortBy

__all__ = ['security_chains']


# Forms

class ChangeMyPasswordForm(BaseForm):

    current_password = fields.PasswordField(
        'Current password',
        [validators.Required()]
    )

    new_password = fields.PasswordField(
        'New password',
        [
            validators.Required(),
            password_validator,
            validators.EqualTo('confirm_password', "Passwords don't match.")
        ]
    )

    confirm_password = fields.PasswordField('Confirm password')

    def validate_current_password(form, field):
        """
        The user must specify their existing password to change their existing
        one.
        """
        user_cls = form._user_cls
        user = getattr(flask.g, user_cls.get_g_key())

        if not field.data:
            return

        if not user.password_eq(field.data):
            raise validators.ValidationError('Password is incorrect.')


# Chains
security_chains = ChainMgr()

# GET
security_chains['get'] = Chain([
    'config',
    'authenticate',
    'init_form',
    'apply_password_rules',
    'get_sessions',
    'decorate',
    'render_template'
])

# POST
security_chains['post'] = Chain([
    'config',
    'authenticate',
    'init_form',
    'apply_password_rules',
    'validate',
    [
        [
            'change_password',
            'redirect'
        ], [
            'get_sessions',
            'decorate',
            'render_template'
        ]
    ]
])

# Define the links
security_chains.set_link(
    factories.config(
        form_cls=ChangeMyPasswordForm,
        open_user_nav=True
    )
)
security_chains.set_link(factories.authenticate())
security_chains.set_link(apply_password_rules())
security_chains.set_link(factories.validate())
security_chains.set_link(factories.render_template('security.html'))
security_chains.set_link(factories.redirect('security'))

@security_chains.link
def decorate(state):
    factories.decorate('security')(state)

    # Modify the breadcrumb
    state.decor['breadcrumbs'] = Nav.local_menu()
    state.decor['breadcrumbs'].add(NavItem('Security', ''))

@security_chains.link
def init_form(state):
    # Initialize the form
    state.form = state.form_cls(flask.request.form)

    # Store the user class against the form
    state.form._user_cls = state.manage_config.frame_cls

@security_chains.link
def change_password(state):
    """Change the current user's password"""
    user_cls = state.manage_config.frame_cls
    user = getattr(flask.g, user_cls.get_g_key())

    # Switch the `new_password` field with password
    form_data = state.form.data
    form_data['password'] = form_data.pop('new_password')

    # Change the password
    user.logged_update(user, form_data)

    # Force a change of session token
    user.sign_in(force_new_token=True)
    flask.session[user_cls.get_session_token_key()] = user.session_token

    # Notify the user that their new password has been set
    flask.flash('New password set.')

@security_chains.link
def get_sessions(state):
    """Get a list of the current user's sessions"""
    user_cls = state.manage_config.frame_cls
    user = getattr(flask.g, user_cls.get_g_key())

    state.user_sessions = user_cls.get_session_cls().many(
        Q.user == user,
        sort=SortBy(Q.last_accessed.desc)
    )
