"""
"""

from .assist import *
from .native import new_dict
from .native import newDate
from .render import *
from .route import *
from .tags import *

# __pragma__ ('noalias')


class UserFun:

    default_account = lambda : new_dict(
        guid=None,
        role=[],
        mail=None,
        name='<none>',
    )

    extract_account = lambda response : new_dict(
        guid=response.data.user_guid,
        role=response.data.user_role,
        mail=response.data.user_mail,
        name=response.data.user_name,
    )

    @staticmethod
    def perform_login(event):
        event.preventDefault()
        local = this
        root = local['$root']
        auth = root['$auth']
        router = root['$router']

        if auth.isAuthenticated():
            auth.logout()
            root.with_account(UserFun.default_account())

        def on_success(response) :
            print(f"session created: {newDate()}")
            account = UserFun.extract_account(response)
            root.with_account(account)
            router.push(Route.home)

        def on_failure(error) :
            UserFun.report_failure(local, error)

        auth.login(new_dict(
            username=local.username,
            password=local.password,
        )).then(on_success, on_failure)

    @staticmethod
    def perform_logout(event):
        event.preventDefault()
        local = this
        root = local['$root']
        auth = root['$auth']
        router = root['$router']

        def on_success(*_) :
            print(f"session deleted: {newDate()}")
            root.with_account(UserFun.default_account())
            router.push(Route.home)

        def on_failure(error) :
            UserFun.report_failure(local, error)

        if auth.isAuthenticated():
            auth.logout().then(on_success, on_failure)

    @staticmethod
    def perform_register(event):
        event.preventDefault()
        local = this
        root = local['$root']
        auth = root['$auth']
        router = root['$router']

        if auth.isAuthenticated():
            auth.logout()
            root.with_account(UserFun.default_account())

        def on_success(*_) :
            router.push(Route.home)

        def on_failure(error) :
            UserFun.report_failure(local, error)

        auth.register(new_dict(
            mailaddr=local.mailaddr,
            username=local.username,
            password1=local.password1,
            password2=local.password2,
        )).then(on_success, on_failure)

    @staticmethod
    def render_update(*_):
        local = this
        store = local['$store']
        local.username = store.state.account.name
        local.mailaddr = store.state.account.mail
        local.original_username = store.state.account.name

    @staticmethod
    def perform_update(event):
        event.preventDefault()
        local = this
        root = local['$root']
        auth = root['$auth']
        router = root['$router']

        if not auth.isAuthenticated():
            router.push(Route.home)
            return

        def on_success(response) :
            print(f"session updated: {newDate()}")
            account = UserFun.extract_account(response)
            root.with_account(account)
            router.push(Route.home)

        def on_failure(error) :
            UserFun.report_failure(local, error)

        opts = new_dict(
            url=auth.options.updateUrl,
        )

        auth.register(new_dict(
            mailaddr=local.mailaddr,
            username=local.username,
            password1=local.password1,
            password2=local.password2,
            original_username=local.original_username,
            original_password=local.original_password,
        ), opts).then(on_success, on_failure)

    @staticmethod
    def report_failure(local, error):
        if hasattr(error, 'response'):
            message = error.response.data.message
        elif hasattr(error, 'message'):
            message = error.message
        else:
            message = 'unknown error'
        local.report_error(True, message)

    @staticmethod
    def report_error(status:bool, message:str):
        local = this
        local.error_status = status
        local.error_message = message
        if status:
            clear_error = lambda *_ : local.report_error(False, "")
            if local.error_timer:
                window.clearTimeout(local.error_timer)
            local.error_timer = window.setTimeout(clear_error, 3000)

    login_data = lambda : new_dict(
        username=None,
        password=None,
        error_timer=None,
        error_status=False,
        error_message=None,
    )

    register_data = lambda : new_dict(
        mailaddr=None,
        username=None,
        password1=None,
        password2=None,
        error_timer=None,
        error_status=False,
        error_message=None,
    )

    update_data = lambda : new_dict(
        original_username=None,
        original_password=None,
        mailaddr=None,
        username=None,
        password1=None,
        password2=None,
        error_timer=None,
        error_status=False,
        error_message=None,
    )

    @staticmethod
    def can_login(*_):
        return this.username and this.password

    @staticmethod
    def can_register(*_):
        return (
            this.mailaddr and
            this.username and
            this.password1 and
            this.password2 and
            True
        )

    @staticmethod
    def can_update(*_):
        has_pass_both = this.password1 and this.password2
        has_pass_none = not this.password1 and not this.password2
        has_pass = has_pass_both or has_pass_none
        return (
            this.mailaddr and
            this.username and
            this.original_username and
            this.original_password and
            has_pass and
            True
        )

    validate_size = "'required|min:4|max:32'"


class UserView:

    form_mail = lambda : FORM_GROUP(FORM_INPUT(
        type="text", name='mailaddr', placeholder="Provide email addreess",
        v_model="mailaddr", v_validate="'required|email'", autocomplete='off',
    ), label="Email address", **RenderFun.bind_input_error('mailaddr'))

    form_user = lambda : FORM_GROUP(FORM_INPUT(
        type="text", name='username', placeholder="Provide account",
        v_model="username", v_validate=UserFun.validate_size, autocomplete='off',
    ), label="User name", **RenderFun.bind_input_error('username'))

    form_pass = lambda : FORM_GROUP(FORM_INPUT(
        type="password", name='password', placeholder="Provide password",
        v_model="password", v_validate=UserFun.validate_size, autocomplete='off',
    ), label="Password entry", **RenderFun.bind_input_error('password'))

    form_pass1 = lambda : FORM_GROUP(FORM_INPUT(
        type="password", name='password1', placeholder="Enter password", ref="passlink",
        v_model="password1", v_validate=UserFun.validate_size, autocomplete='off',
    ), label="Password entry", **RenderFun.bind_input_error('password1'))

    form_pass2 = lambda : FORM_GROUP(FORM_INPUT(
        type="password", name='password2', placeholder="Confirm password",
        v_model="password2", v_validate="'required|confirmed:passlink'", autocomplete='off',
    ), label="Password confirmation", **RenderFun.bind_input_error('password2'))

    original_user = lambda : FORM_GROUP(FORM_INPUT(
        type="text", name='original_username', placeholder="Provide account", disabled='',
        v_model="original_username", v_validate=UserFun.validate_size, autocomplete='off',
    ), label="Original username", **RenderFun.bind_input_error('original_username'))

    original_pass = lambda : FORM_GROUP(FORM_INPUT(
        type="password", name='original_password', placeholder="Provide password",
        v_model="original_password", v_validate=UserFun.validate_size, autocomplete='off',
    ), label="Original password", **RenderFun.bind_input_error('original_password'))

    entry_login = lambda : [FONT_ICON(icon='sign-in-alt'), SPAN('Login', cls='ml-2')]
    entry_logout = lambda : [FONT_ICON(icon='sign-out-alt'), SPAN('Logout', cls='ml-2')]
    entry_update = lambda : [FONT_ICON(icon='user-edit'), SPAN('Update', cls='ml-2')]
    entry_register = lambda : [FONT_ICON(icon='user-plus'), SPAN('Register', cls='ml-2')]
    entry_manager = lambda : [FONT_ICON(icon='user-shield'), SPAN('Manager', cls='ml-2')]


class UserLoginUnit:

    tag = produce_tag('user-login-unit')

    form_button = lambda : FORM_GROUP(BUTTON(
        'Login', type="submit",
    ), **RenderFun.bind_submit_disable())

    form_body = lambda : [
        UserView.form_user(), UserView.form_pass(), UserLoginUnit.form_button(),
    ]

    template = lambda : DIV([
        ALERT(UserView.entry_login(), show='', fade='', variant="info"),
        CONTAINER([
            FORM(UserLoginUnit.form_body(), v_on_submit='submit_action',),
            LINK('Register', to=Route.Account.register,
                 **RenderFun.use_tooltip('register instead of login')
            ),
            MODAL('Login failure: {{error_message}}',
                ok_only='', v_model='error_status', **RenderFun.use_header(),
            ),
        ], **RenderFun.use_width()),
    ]).outerHTML

    arkon = lambda : window.Vue.component(name_of_tag(UserLoginUnit.tag), new_dict(
        data=UserFun.login_data,
        methods=new_dict(
            has_input=UserFun.can_login,
            submit_action=UserFun.perform_login,
            report_error=UserFun.report_error,
        ),
        template=UserLoginUnit.template(),
    ))


UserLoginUnit.arkon()


class UserLogoutUnit:

    tag = produce_tag('user-logout-unit')

    form_user = lambda : FORM_GROUP(FORM_INPUT(
        type="text", name='username', disabled='',
        v_model="$store.state.account.name",
    ), label="User name",)

    form_button = lambda : FORM_GROUP(BUTTON(
        'Logout', type="submit", ref='form_button',
    ),)

    form_body = lambda : [
        UserLogoutUnit.form_user(), UserLogoutUnit.form_button(),
    ]

    template = lambda : DIV([
        ALERT(UserView.entry_logout(), show='', fade='', variant="warning"),
        CONTAINER([
            FORM(UserLogoutUnit.form_body(), v_on_submit='submit_action',),
        ], **RenderFun.use_width()),
    ]).outerHTML

    arkon = lambda : window.Vue.component(name_of_tag(UserLogoutUnit.tag), new_dict(
        methods=new_dict(
            submit_action=UserFun.perform_logout,
            internal_logout=lambda : this['$refs'].form_button.click(),
            report_error=UserFun.report_error,
        ),
        template=UserLogoutUnit.template(),
    ))


UserLogoutUnit.arkon()


class UserUpdateUnit:

    tag = produce_tag('user-update-unit')

    form_button = lambda : FORM_GROUP(BUTTON(
        'Update', type="submit",
    ), **RenderFun.bind_submit_disable())

    form_body = lambda : [
        UserView.form_mail(), UserView.form_user(),
        UserView.form_pass1(), UserView.form_pass2(),
        ALERT([UserView.original_user(), UserView.original_pass(), ], variant='primary', show=''),
        UserUpdateUnit.form_button(),
    ]

    template = lambda : DIV([
        ALERT(UserView.entry_update(), show='', fade='', variant="primary"),
        CONTAINER([
            FORM(UserUpdateUnit.form_body(), v_on_submit='submit_action',),
            MODAL('Update failure: {{error_message}}',
                ok_only='', v_model='error_status', **RenderFun.use_header(),
            ),
        ], **RenderFun.use_width()),
    ]).outerHTML

    arkon = lambda : window.Vue.component(name_of_tag(UserUpdateUnit.tag), new_dict(
        data=UserFun.update_data,
        created=UserFun.render_update,
        methods=new_dict(
            has_input=UserFun.can_update,
            submit_action=UserFun.perform_update,
            report_error=UserFun.report_error,
        ),
        template=UserUpdateUnit.template(),
    ))


UserUpdateUnit.arkon()


class UserRegisterUnit:

    tag = produce_tag('user-register-unit')

    form_button = lambda : FORM_GROUP(BUTTON(
        'Register', type="submit",
    ), **RenderFun.bind_submit_disable())

    form_body = lambda : [
        UserView.form_mail(), UserView.form_user(),
        UserView.form_pass1(), UserView.form_pass2(),
        UserRegisterUnit.form_button(),
    ]

    template = lambda : DIV([
        ALERT(UserView.entry_register(), show='', fade='', variant="primary"),
        CONTAINER([
            FORM(UserRegisterUnit.form_body(), v_on_submit='submit_action',),
            LINK('Login', to=Route.Account.login,
                **RenderFun.use_tooltip('login instead of register')
            ),
            MODAL('Registration failure: {{error_message}}',
                ok_only='', v_model='error_status', **RenderFun.use_header(),
            ),
        ], **RenderFun.use_width()),
    ]).outerHTML

    arkon = lambda : window.Vue.component(name_of_tag(UserRegisterUnit.tag), new_dict(
        data=UserFun.register_data,
        methods=new_dict(
            has_input=UserFun.can_register,
            submit_action=UserFun.perform_register,
            report_error=UserFun.report_error,
        ),
        template=UserRegisterUnit.template(),
    ))


UserRegisterUnit.arkon()


class UserManagerUnit:

    tag = produce_tag('user-manager-unit')

    template = lambda : DIV([
        ALERT(UserView.entry_manager(), show='', fade='', variant="primary"),
    ]).outerHTML

    arkon = lambda : window.Vue.component(name_of_tag(UserManagerUnit.tag), new_dict(
        methods=new_dict(
        ),
        template=UserManagerUnit.template(),
    ))
