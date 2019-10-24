"""
Enable multi-factor authentication (MFA) for the user.
"""

from datetime import datetime
import io

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.forms import BaseForm, fields, validators
from manhattan.manage.views import factories, utils
from manhattan.nav import NavItem
from manhattan.secure import random_code
import pyotp
import qrcode
import qrcode.image.svg

__all__ = ['enable_chains']


# Forms

class EnableForm(BaseForm):

    otp_secret = fields.HiddenField()

    totp = fields.StringField(
        'Your six-digit code',
        [validators.Required()]
    )

    def validate_totp(form, field):

        if not field.data:
            return

        if not pyotp.TOTP(form.otp_secret.data).verify(field.data):
            raise validators.ValidationError('Not a valid code')


# Chains
enable_chains = ChainMgr()

# POST
enable_chains['get'] = Chain([
    'config',
    'authenticate',
    'init_form',
    'generate_qr_code',
    'decorate',
    'render_template'
])

# POST
enable_chains['post'] = Chain([
    'config',
    'authenticate',
    'init_form',
    'generate_qr_code',
    'validate',
    [
        [
            'enable_mfa',
            'redirect'
        ], [
            'decorate',
            'render_template'
        ]
    ]
])

# Define the links
enable_chains.set_link(
    factories.config(
        form_cls=EnableForm,
        open_user_nav=True
    )
)
enable_chains.set_link(factories.authenticate(mfa_required=False))
enable_chains.set_link(factories.init_form())
enable_chains.set_link(factories.validate())
enable_chains.set_link(factories.render_template('mfa/enable.html'))
enable_chains.set_link(factories.redirect('mfa_recovery_codes'))

@enable_chains.link
def decorate(state):
    state.decor = utils.base_decor(state.manage_config, 'mfa_enable')
    state.decor['title'] = 'Enable 2-factor authentication'

    # Breadcumbs
    state.decor['breadcrumbs'].add(
        NavItem('Security', state.manage_config.get_endpoint('security'))
    )
    state.decor['breadcrumbs'].add(
        NavItem('Enable 2-factor authentication', '')
    )

@enable_chains.link
def generate_qr_code(state):
    """
    Generate a secret and QR code to allow a user to verify they have enabled
    QR on their device.
    """
    user_cls = state.manage_config.frame_cls
    user = getattr(flask.g, user_cls.get_g_key())
    prefix = user_cls.get_settings_prefix()

    # Make sure we have a secret for generating time-based one time passwords
    state.otp_secret = state.form.data.get('otp_secret') \
            or pyotp.random_base32()

    state.form.otp_secret.data = state.otp_secret

    # Generate the provisioning URL
    mfa_client = pyotp.totp.TOTP(state.otp_secret)
    mfa_provisision_uri = mfa_client.provisioning_uri(
        user.email,
        issuer_name=flask.current_app.config[f'{prefix}_MFA_ISSUER']
    )

    # Generate the QR code as an SVG
    f = io.BytesIO()
    qrcode.make(
        mfa_provisision_uri,
        image_factory=qrcode.image.svg.SvgPathImage
    ).save(f)
    f.seek(0)

    state.qr_image = f.read().decode('utf8')

@enable_chains.link
def enable_mfa(state):
    """Enable multi-factor authentication for the user"""
    user_cls = state.manage_config.frame_cls
    user = getattr(flask.g, user_cls.get_g_key())
    prefix = user_cls.get_settings_prefix()

    # Generate recovery codes
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

    # Enable MFA fo
    user.logged_update(
        user,
        {
            'mfa_enabled': True,
            'mfa_otp_secret': state.otp_secret,
            'mfa_recovery_codes': recovery_codes
        },
        'mfa_enabled',
        'mfa_otp_secret',
        'mfa_recovery_codes',
        'modified'
    )

    # Update the users sessions MFA authorized date/time
    flask.current_session = user.current_session
    flask.current_session.mfa_authorized = datetime.utcnow()
    flask.current_session.update('mfa_authorized')
