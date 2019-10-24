from datetime import datetime
import secrets

import flask
from manhattan.comparable import ComparableFrame
from manhattan.formatters.text import remove_accents
from manhattan.secure import encrypt_password, random_token
from mongoframes import ASC, In, IndexModel, Q, SortBy
import pyotp

__all__ = ['BaseUser']


class BaseUser(ComparableFrame):
    """
    The `BaseUser` collection provides user access / control to manhattan
    manage applications.

    NOTE: This is a **base** class and should not be used directly, instead
    define a new `User` class for your project that inherits from this class.
    """

    _fields = {

        # The name of the user
        'first_name',
        'last_name',

        # A lowercase version of the user's full name (for searching)
        'full_name_lower',

        # The user's email address
        'email',

        # A lowercase version of the user's email (for lookup and indexing)
        'email_lower',

        # Flag indicating the date/time a user was last sent an invite to the
        # application.
        'invited',

        # A unique token assigned to the user when invited, the token is used
        # to identify the user (as a parameter) to accept their invite.
        'invite_token',

        # Flag indicating the date/time a user accepted their invite
        'invite_accepted',

        # A hashed version of the user's password used in combination with the
        # user's salt to verify a password when supplied by the user.
        'password_hash',

        # A random string used
        'password_salt',

        # A flag indicating the date/time a user requested a reset password
        # link.
        'password_reset_requested',

        # A unique token assigned to the user when they request a password
        # reset link, the token is used to identify the user (as a parameter)
        # to set a new password.
        'password_reset_token',

        # The session token identifying the user to the manage application
        # (the session token is generated when the user signs-in and stored
        # in the secure session cookie).
        'session_token',

        # MFA (Multi-factor authentication) fields

        # Flag indicating if MFA has been enabled for this user
        'mfa_enabled',

        # The secret used to generate and verify MFA time-based one time
        # passwords (TOTP) for this user. This key is registered with an
        # authentication device (such as a mobile phone app) and then used by
        # both the app and the device to generate a TOTP.
        'mfa_otp_secret',

        # A list of emergency one time passwords for the user created when
        # multi-factor authentication is enabled.
        'mfa_recovery_codes'
    }

    _private_fields = ComparableFrame._private_fields | {
        'email_lower',
        'full_name_lower',
        'invited',
        'invite_accepted',
        'invite_token',
        'mfa_recovery_codes',
        'mfa_otp_secret',
        'password_hash',
        'password_reset_requested',
        'password_reset_token',
        'password_salt',
        'session_token'
    }

    _uncompared_fields = ComparableFrame._uncompared_fields | {
        'email_lower',
        'full_name_lower',
        'invited',
        'invite_accepted',
        'invite_token',
        'mfa_recovery_codes',
        'mfa_otp_secret',
        'password_reset_requested',
        'password_reset_token',
        'password_salt',
        'session_token'
    }

    _recommended_indexes = [
        IndexModel([('email_lower', ASC)], unique=True),
        IndexModel([('invite_token', ASC)], unique=True, sparse=True),
        IndexModel(
            [('password_reset_token', ASC)],
            unique=True,
            sparse=True
            ),
        IndexModel([('session_token', ASC)], unique=True, sparse=True)
    ]

    def __str__(self):
        return f'{self.full_name} <{self.email}>'

    # Properties

    @property
    def current_session(self):
        return self.get_session_cls().get_current_session(self._id)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def last_accessed(self):
        user_session = self.get_session_cls().one(
            Q.user == self._id,
            sort=SortBy(Q.last_accessed.desc),
            projection={'last_accessed': True}
        )
        if user_session:
            return user_session.last_accessed

    @property
    def mfa_authorized(self):
        current_session = self.get_session_cls().get_current_session(
            self._id,
            projection={'mfa_authorized': True}
        )
        return current_session and current_session.mfa_authorized is not None

    @property
    def password(self):
        # The 'password' property however be used to retrieve a password only
        # to set one.
        return ''

    @password.setter
    def password(self, value):
        # Requests to set the password to a none value (e.g '', or None) will
        # be ignored.
        if value in [None, '']:
            return

        # Create a random salt for the password
        self.password_salt = secrets.token_urlsafe(64)

        # Set the password
        prefix = self.get_settings_prefix()
        iterations = flask\
            .current_app\
            .config[f'{prefix}_PASSWORD_HASH_ITERATIONS']
        self.password_hash = encrypt_password(
            value,
            self.password_salt,
            iterations=iterations
        )

        # Set the user as having accepted an invite
        if not self.invited:
            self.invited = datetime.now()
        self.invite_accepted = True

    # Methods

    def generate_mfa_otp_provisioning_uri(self):
        """
        Generate a URI for provisioning multi-factor autentication for this
        user (this URL is used to generate a QR code that can be scanned by
        an authentication app such as Google authenticator).
        """
        prefix = self.get_settings_prefix()
        return pyotp.TOTP(self.mfa_otp_secret).provisioning_uri(
            self.email,
            issuer_name=current_app.config[f'{prefix}_MFA_ISSUER']
        )

    def mfa_topt_eq(self, password):
        """Verify a time-based one time password for the user"""
        return pyotp.TOTP(self.mfa_otp_secret).verify(password)

    def password_eq(self, password):
        """Check if a password is equal to the user's password"""
        prefix = self.get_settings_prefix()
        iterations = flask\
            .current_app\
            .config[f'{prefix}_PASSWORD_HASH_ITERATIONS']
        password_hash = encrypt_password(
            password,
            self.password_salt,
            iterations=iterations
        )
        return self.password_hash == password_hash

    def sign_in(self, force_new_token=False):
        """
        Sign a user in. The function returns the user session and a flag
        indicating if a new session (device) was created (True) or an existing
        known session (device) was used (False).
        """

        # Sign the user in against a session
        user_session, new_session = self.get_session_cls().sign_in(self._id)

        # Re-use an existing session token if available and not expired
        last_accessed = self.last_accessed
        if last_accessed:

            age = datetime.utcnow() - last_accessed
            prefix = self.get_settings_prefix()

            if age > flask.current_app.config[f'{prefix}_SESSION_LIFESPAN']:

                # The session token has expired remove it so a new one is
                # generated.
                self.session_token = None

        if not self.session_token or force_new_token:

            # No existing session token so create a new one
            self.session_token = random_token()

        self.update('session_token')

        return (user_session, new_session)

    # Class methods

    # Sessions management

    @classmethod
    def from_session(cls, projection=None):
        """Return a user from the current session token"""

        # Do we have session token?
        session_token = flask.session.get(cls.get_session_token_key())
        if not session_token:
            return None

        # Is the session token valid?
        user = cls.one(
            Q.session_token == session_token,
            projection=projection
        )
        if not user:
            return None

        # Verify the session/device
        prefix = cls.get_settings_prefix()
        lifespan = flask.current_app.config[f'{prefix}_SESSION_LIFESPAN']
        if not cls.get_session_cls().verify_access(user._id, lifespan):
            return None

        return user

    @classmethod
    def get_g_key(cls):
        """
        Return the key used to store an instance of the user against the
        global context (`flask.g`).
        """
        return 'user'

    @classmethod
    def get_session_cls(cls):
        """Return the session class that will be used by the user"""
        raise NotImplemented()

    @classmethod
    def get_session_token_key(cls):
        """
        Get the session token key used to store/retrieve the user's session
        token in the flask session.
        """
        return 'manage_session_token'

    @classmethod
    def get_settings_prefix(cls):
        """Return the prefix for settings properties for the user"""
        return 'USER'

    # Failed sign-ins

    @classmethod
    def get_sign_in_attempt_key(cls, email):
        """
        Return a key that can be used to store and retrieve the number of
        failed sign-in attempts for a given email against this application.
        """
        server_name = flask.current_app.config['SERVER_NAME']
        return f'user_failed_login:{server_name}:{email.lower()}'

    @classmethod
    def is_locked_out(cls, email):
        """
        Return True if the given email is locked out (cannot be used to
        sign-in until the lock is removed or expires.)
        """
        config = flask.current_app.config
        prefix = cls.get_settings_prefix()
        cache = config[f'{prefix}_FAILED_SIGN_IN_CACHE']
        return (cache.get(cls.get_sign_in_attempt_key(email)) or 0) \
                >= config[f'{prefix}_MAX_FAILED_SIGN_IN_ATTEMPTS']

    # Static methods

    @staticmethod
    def _on_upsert(sender, frames):
        for frame in frames:

            if frame.email:

                # Store lowercase email
                frame.email_lower = frame.email.lower()

            if frame.first_name and frame.last_name:

                # Store lowercase full name
                frame.full_name_lower = frame.full_name.replace(',','').lower()
                frame.full_name_lower = remove_accents(frame.full_name_lower)

    @staticmethod
    def _on_delete(sender, frames):

        # Delete any associated user sessions
        user_cls = sender.get_session_cls()
        user_cls.delete_many(
            user_cls.many(In(Q.user, [f._id for f in frames]))
        )

