"""
Link factories for manhattan views.
"""


import bson
import json
import os
import urllib.parse as urlparse
from urllib.parse import urlencode

import flask
import inflection
from manhattan import secure
from manhattan.nav import Nav, NavItem
from manhattan.manage.views import utils

# Optional imports
try:
    from manhattan.assets import Asset
    from manhattan.assets.fields import AssetField
    from manhattan.assets.transforms.base import BaseTransform
    __assets_supported__ = True

except ImportError as e:
    __assets_supported__ = False

__all__ = [
    'authenticate',
    'config',
    'decorate',
    'get_document',
    'init_form',
    'mfa_authenticate',
    'redirect',
    'render_template',
    'store_assets',
    'validate'
    ]


def authenticate(
        user_g_key='user',
        sign_in_endpoint='manage_users.sign_in',
        sign_out_endpoint='manage_users.sign_out',
        mfa_required=None,
        mfa_authorize_endpoint='manage_users.mfa_auth',
        mfa_authorized_attr='mfa_authorized',
        mfa_enable_endpoint='manage_users.mfa_enable',
        mfa_enabled_attr='mfa_enabled',
    ):
    """
    Authenticate the caller has permission to call the view.

    This link adds a `user` key to the the state containing the currently
    signed in user.
    """

    def authenticate(state):
        # Get the signed in user
        state.manage_user = flask.g.get(user_g_key)

        # Extract the full path (we use this approach to cater for the
        # dispatcher potentially modifying the URL root value).
        parts = urlparse.urlparse(flask.request.url)
        full_path = flask.request.url.split(parts[1], 1)[1]

        # We're not allowed to access this view point so determine if that's
        # because we're not sign-in or because we don't have permission.
        if not state.manage_user:
            # We need to sign-in to view this endpoint

            # Forward the user to the sign-in page with the requested URL as
            # the `next` parameter.
            redirect_url = flask.url_for(
                sign_in_endpoint,
                next=secure.safe_redirect_url(
                    full_path,
                    [flask.url_for(sign_out_endpoint)]
                )
            )
            return flask.redirect(redirect_url)

        # Check that any user with multi-factor authentication (MFA) enabled
        # has authorized their session using MFA.
        if getattr(state.manage_user, mfa_enabled_attr, None):
            if not getattr(state.manage_user, mfa_authorized_attr, None):

                # The user needs to MFA authorize their session to view this
                # endpoint.

                # Forward the user to the MFA auth page with the requested URL
                # as the `caller` parameter.
                redirect_url = flask.url_for(
                    mfa_authorize_endpoint,
                    caller_url=full_path
                )

                return flask.redirect(redirect_url)

        # Check if the application requires multi-factor authentication (MFA)
        # to be enabled for users. If so and a user doesn't have MFA enabled
        # then we redirect them to enable MFA.
        _mfa_required = mfa_required
        if _mfa_required is None:
            _mfa_required = flask.current_app.config.get('USER_MFA_REQUIRED')

        if _mfa_required:
            if not getattr(state.manage_user, mfa_enabled_attr, None):
                return flask.redirect(flask.url_for(mfa_enable_endpoint))

        # Check if we're allowed to access this requested endpoint
        if not Nav.allowed(flask.request.endpoint, **flask.request.view_args):

            # We don't have permission to view this endpoint
            flask.abort(403, 'Permission denied')

    return authenticate

def config(**defaults):
    """
    Return a function will configure a view's state adding defaults where no
    existing value currently exists in the state.

    This function is designed to be included as the first link in a chain and
    to set the initial state so that chains can be configured on a per copy
    basis.
    """

    def config(state):
        # Apply defaults
        for key, value in defaults.items():

            # First check if a value is already set against the state
            if key in state:
                continue

            # If not then set the default
            state[key] = value

    return config

def decorate(view_type, title=None, last_breadcrumb=None):
    """
    Return a function that will add decor information to the state for the
    named view.
    """

    def decorate(state):
        document = state.get(state.manage_config.var_name)
        state.decor = utils.base_decor(state.manage_config, state.view_type)

        # Title
        if document:
            state.decor['title'] = '{action} {target}'.format(
                action=inflection.humanize(view_type),
                target=state.manage_config.titleize(document)
            )
        else:
            state.decor['title'] = inflection.humanize(view_type)

        # Breadcrumbs
        if Nav.exists(state.manage_config.get_endpoint('list')):
            state.decor['breadcrumbs'].add(
                utils.create_breadcrumb(state.manage_config, 'list')
            )
        if Nav.exists(state.manage_config.get_endpoint('view')) and document:
            state.decor['breadcrumbs'].add(
                utils.create_breadcrumb(state.manage_config, 'view', document)
            )
        state.decor['breadcrumbs'].add(NavItem('Update'))

    return decorate

def get_document(projection=None):
    """
    Return a function that will attempt to retreive a document from the
    database by `_id` using the `var_name` named parameter in the request.

    This link adds a `{state.manage_config.var_name}` key to the the state
    containing the document retreived.

    Optionally a projection to use when getting the document can be specified,
    if no projection is specified then the function will look for a projection
    against the state (e.g state.projection).
    """

    def get_document(state):
        # Get the Id of the document passed in the request
        document_id = flask.request.values.get(state.manage_config.var_name)

        # Attempt to convert the Id to the required type
        try:
            document_id = bson.objectid.ObjectId(document_id)
        except bson.errors.InvalidId:
            flask.abort(404)

        # Attempt to retrieve the document
        by_id_kw = {}
        if projection or state.projection:
            by_id_kw['projection'] = projection or state.projection

        document = state.manage_config.frame_cls.by_id(
            document_id,
            **by_id_kw
        )

        if not document:
            flask.abort(404)

        # Set the document against the state
        state[state.manage_config.var_name] = document

    return get_document

def init_form(populate_on=None):
    """
    Return a function that will initialize a form for the named generic view
    (e.g list, add, update, etc.) or the given form class.

    This link adds a `form` key to the the state containing the initialized
    form.
    """

    # If populate_on is not specified then we default to `POST`
    if populate_on is None:
        populate_on = ['POST']

    def init_form(state):
        # Get the form class
        assert state.form_cls, 'No form class `form_cls` defined'

        # Initialize the form
        form_data = None
        if flask.request.method in populate_on:
            if flask.request.method in ['POST', 'PUT']:
                form_data = flask.request.form
            else:
                form_data = flask.request.args

        # If a document is assign to the state then this is sent as the first
        # argument when initializing the form.
        obj = None
        if state.manage_config.var_name in state:
            obj = state[state.manage_config.var_name]

        # Initialize the form
        state.form = state.form_cls(form_data or None, obj=obj)

    return init_form

def mfa_authenticate_scoped_session(
    authorize_endpoint='manage_users.mfa_auth',
    enabled_attr='mfa_enabled',
    get_cache=None
):
    """
    Return a function that creates an authorized 2-factor authenticated
    session.

    This link should be added after the `authenticate` link.
    """

    if get_cache is None:
        get_cache = lambda s: \
                flask.current_app.config['USER_MFA_SCOPED_SESSION_CACHE']

    def mfa_authenticate_scoped_session(state):

        if getattr(state.manage_user, enabled_attr, None):

            # Generate the caller URL

            # Extract the full path (we use this approach to cater for the
            # dispatcher potentially modifying the URL root value).
            parts = urlparse.urlparse(flask.request.url)
            full_path = flask.request.url.split(parts[1], 1)[1]

            # Parse URL
            caller_url_parts = list(urlparse.urlparse(full_path))

            # Remove 'mfa_scoped_session_token' from the query parameters
            query = dict(urlparse.parse_qsl(caller_url_parts[4]))
            query.pop('mfa_scoped_session_token', None)
            caller_url_parts[4] = urlencode(query)

            # Rebuild the URL
            caller_url = urlparse.urlunparse(caller_url_parts)

            # Check if a scoped session has been authorized using MFA
            session_token \
                    = flask.request.values.get('mfa_scoped_session_token')

            if session_token:

                # Verify the scoped session
                verified = secure.mfa.verify_scoped_session(
                    get_cache(state),
                    session_token,
                    (str(state.manage_user._id), caller_url)
                )
                if verified:
                    return

                # Notify the user that their session likely expired
                flask.flash('2FA session expired', 'error')

            # Redirect the user to verify the session
            return flask.redirect(
                flask.url_for(
                    authorize_endpoint,
                    caller_url=caller_url,
                    scoped=True
                )
            )

    return mfa_authenticate_scoped_session


def mfa_end_scoped_session(
    authorize_endpoint='manage_users.mfa_auth',
    enabled_attr='mfa_enabled',
    get_cache=None
):
    """
    Return a function that will clear a scoped session.

    This link should be added as the penultimate link, e.g before `redirect`
    or `render_template`.
    """

    if get_cache is None:
        get_cache = lambda s: \
                flask.current_app.config['USER_MFA_SCOPED_SESSION_CACHE']

    def mfa_end_scoped_session(state):
        secure.mfa.delete_scoped_session(
            get_cache,
            flask.request.values.get('mfa_scoped_session_token')
        )

    return mfa_end_scoped_session

def redirect(endpoint, include_id=False):
    """
    Return a function that will trigger a redirect to the given endpoint.

    Optionally an Id for the current document in the state can be added to the
    URL, e.g `url_for('view.user', user=user._id)` by passing `include_id` as
    True.
    """

    def redirect(state):
        # Build the URL arguments
        url_args = {}
        if include_id:
            url_args[state.manage_config.var_name] = \
                    state[state.manage_config.var_name]._id

        # Get the URL for the endpoint
        prefix = state.manage_config.endpoint_prefix
        if state.manage_config.endpoint_prefix:
            url = flask.url_for('.' + prefix + endpoint, **url_args)
        else:
            url = flask.url_for('.' + endpoint, **url_args)

        # Return the redirect response
        return flask.redirect(url)

    return redirect

def render_template(template_path):
    """
    Return a function that will render the named template. The state object is
    used as template arguments.
    """

    def render_template(state):
        # Build the template filepath
        full_template_path = os.path.join(
            state.manage_config.template_path,
            template_path
        )

        # Render the template
        return flask.render_template(full_template_path, **state)

    return render_template

def store_assets():
    """
    Return a function that will store changes to assets.
    """

    def store_assets(state):

        assert __assets_supported__, \
            'This link requires manhattan-assets to be installed'

        # Check that the app supports an asset manager, if not then there's
        # nothing to do.
        if not hasattr(flask.current_app, 'asset_mgr'):
            return
        asset_mgr = flask.current_app.asset_mgr

        # Get the document being added or updated
        document = state[state.manage_config.var_name]

        # Look for asset fields against the document, convert temporary assets
        # to permenant assets and check for changes to the base transform which
        # require any existing variations for the asset to be re-generated.

        new_assets = []
        updated_assets = []
        removed_assets = []

        for field in document.get_fields():

            # This must relate to a field within the form
            if field not in state.form:
                continue

            # We're only interested in fields that hold assets
            if not isinstance(state.form[field], AssetField):
                continue

            value = state.form_data.get(field)

            # Check if the asset is new
            if value:
                if value.temporary:

                    # Store the asset permenantly
                    flask.current_app.asset_mgr.store(value)

                    # Log that we need to
                    new_assets.append(field)

                    continue

                # Check if the base transforms for the asset have been modified
                if state.form[field].base_transform_modified:
                    updated_assets.append(field)

            else:
                removed_assets.append(field)

        # Analyze and generate variations for new and updated assets

        # Analyzers
        for field in new_assets:
            value = state.form_data.get(field)
            analyzers = state.manage_config.asset_analyzers.get(field, [])
            if analyzers:
                asset_mgr.analyze(value, analyzers)

        # Variations
        for field in (new_assets + updated_assets):
            value = state.form_data.get(field)

            variations = state.manage_config.asset_variations.get(field, {})

            # Check for existing variations (which overide any variation set
            # against the manage config).
            if value.variations:
                for name, variation_asset in value.variations.items():
                    variations[name] = [BaseTransform.from_json_type(t)
                        for t in variation_asset.local_transforms]

            # Ensure the draft variation is never updated
            if '--draft--' in variations:
                variations.pop('--draft--')

            if variations:

                # Get the list of base transforms for the asset
                base_transforms = [BaseTransform.from_json_type(t)
                        for t in value.base_transforms]

                # Store variations for the asset
                asset_mgr.generate_variations(
                    value,
                    variations,
                    base_transforms
                )

        # Save any changes to the database
        update_fields = new_assets + updated_assets + removed_assets

        if update_fields:

            # Check to see if the frame class supports `logged_update`s and if
            # so...
            if hasattr(state.manage_config.frame_cls, 'logged_update'):

                # Supports `logged_update`
                document.logged_update(
                    state.manage_user,
                    {
                        f: state.form_data.get(f)._document \
                        if state.form_data.get(f) else None \
                        for f in update_fields
                    }
                )

            else:

                # Doesn't support `logged_update`
                for field in update_fields:
                    setattr(document, field, state.form_data.get(field))

                document.update(*update_fields)

    return store_assets

def validate(error_msg='Please review your submission'):
    """
    Return a function that will call validate against `state.form`. If the form
    is valid the function will return `True` or `False` if not.

    Optionally an `error_msg` can be passed, if the form fails to validate this
    will be flashed to the user.
    """

    def validate(state):
        assert state.form, 'No form to validate against'

        if state.form.validate():
            return True

        flask.flash(error_msg, 'error')
        return False

    return validate
