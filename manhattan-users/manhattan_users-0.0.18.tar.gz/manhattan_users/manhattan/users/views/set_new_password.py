"""
Allow users to set a new password.
"""

from datetime import datetime

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.comparable.change_log import ChangeLogEntry
from manhattan.forms import BaseForm, fields, validators
from manhattan.manage.views import factories, utils
from manhattan.users.utils import apply_password_rules, password_validator
from mongoframes import Q

__all__ = ['set_new_password_chains']


# Forms

class SetNewPasswordForm(BaseForm):

    reset_token = fields.HiddenField()

    password = fields.PasswordField(
        'Password',
        [
            validators.Required(),
            password_validator,
            validators.EqualTo('confirm_password', "Passwords don't match.")
        ]
    )

    confirm_password = fields.PasswordField('Confirm password')


# Chains
set_new_password_chains = ChainMgr()

# GET
set_new_password_chains['get'] = Chain([
    'config',
    'init_form',
    'apply_password_rules',
    'get_user',
    'decorate',
    'render_template'
])

# POST
set_new_password_chains['post'] = Chain([
    'config',
    'init_form',
    'apply_password_rules',
    'get_user',
    'validate',
    [
        [
            'set_password',
            'sign_in',
            'redirect'
        ],
        [
            'decorate',
            'render_template'
        ]
    ]
])

# Define the links
set_new_password_chains.set_link(
    factories.config(form_cls=SetNewPasswordForm)
)
set_new_password_chains.set_link(factories.init_form())
set_new_password_chains.set_link(apply_password_rules())
set_new_password_chains.set_link(factories.validate())
set_new_password_chains.set_link(
    factories.render_template('set_new_password.html')
)
set_new_password_chains.set_link(factories.redirect('dashboard'))

@set_new_password_chains.link
def decorate(state):
    state.decor = utils.base_decor(state.manage_config, 'set_new_password')
    state.decor['title'] = 'Set new password'

@set_new_password_chains.link
def get_user(state):
    """
    Get the user who is setting a new password based on their reset token.
    """
    user_cls = state.manage_config.frame_cls
    prefix = user_cls.get_settings_prefix()

    reset_password_url = flask.url_for(
        state.manage_config.get_endpoint('reset_password')
    )

    reset_token = flask.request.values.get('reset_token', '').strip()
    if not reset_token:

        # The token was provided, notify the user and redirect them to request
        # a new reset link.
        flask.flash(
            'Not a valid reset password link, no reset token provided.',
            'warning'
        )
        return flask.redirect(reset_password_url)

    # Get the user by their reset token
    user = user_cls.one(Q.password_reset_token == reset_token)
    state[state.manage_config.var_name] = user

    if not user:

        # No user found for the reset token, notify the user and redirect
        # them to request a new reset link.
        flask.flash(
            (
                'Not a valid reset password link, the reset token does not '
                'exist.'
            ),
            'warning'
        )
        return flask.redirect(reset_password_url)

    reset_lifespan = flask\
        .current_app\
        .config[f'{prefix}_PASSWORD_RESET_LIFESPAN']
    ellapsed = datetime.utcnow() - user.password_reset_requested

    if ellapsed > reset_lifespan:

        # The invite has expired, notify the user and redirect them to request
        # a new invite.
        flask.flash(
            (
                'It appears this reset password link has expired please  '
                'request a new one.'
            ),
            'warning'
        )
        return flask.redirect(reset_password_url)

    if user_cls.is_locked_out(user.email):

        # The user is currently locked out for too many failed attempts to
        # sign-in attempts, notify the user and redirect them to the set new
        # password page.
        lockout = flask.current_app.config[f'{prefix}_FAILED_SIGN_IN_LOCKOUT']
        minutes = round(lockout.total_seconds() / 60)
        flask.flash(
            f'Your account is locked out due to too many failed sign '
            f'in attempts, please try again in {minutes} minutes.',
            'error'
        )
        return flask.redirect(
            flask.url_for(state.manage_config.get_endpoint('sign_in'))
        )

@set_new_password_chains.link
def set_password(state):
    """Set a new password for a user"""
    user_cls = state.manage_config.frame_cls
    user = state[state.manage_config.var_name]

    # Set the user's password
    user.password = state.form.data['password']
    user.update()

    # Log the change
    entry = ChangeLogEntry({
        'type': 'NOTE',
        'documents': [user],
        'user': user
    })
    entry.add_note('Password reset')
    entry.insert()

    # Unset the invite and reset password token fields so the reset link and
    # any outstanding invite link can't be (re)used.
    user_cls.get_collection().update(
        {'_id': user._id},
        {'$unset': {'invite_token': '', 'password_reset_token': ''}}
    )

@set_new_password_chains.link
def sign_in(state):
    """Sign the user in after they have reset their password"""
    user_cls = state.manage_config.frame_cls
    user = state[state.manage_config.var_name]

    user.sign_in(force_new_token=True)
    flask.session[user_cls.get_session_token_key()] = user.session_token
