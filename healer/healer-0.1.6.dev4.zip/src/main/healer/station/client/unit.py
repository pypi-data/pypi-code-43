"""
"""

from .assist import *
from .dual_list import *
from .native import *
from .route import *
from .tags import *
from .user import *

# __pragma__ ('noalias', 'name')
# __pragma__ ('noalias', 'type')


class ArkonNav:

    left_list = lambda : [
        NAV_ITEM('Home', to=Route.home),
        NAV_ITEM('About', to=Route.about),
    ]

    form_body = lambda : [
        FORM_INPUT('', size="sm", cls="mr-sm-2", placeholder="Search"),
        BUTTON('Search', size="sm", cls="my-2 my-sm-0", type="submit"),
    ]

    lang_drop = lambda : [
        DROP_ITEM('EN'),
        DROP_ITEM('RU'),
    ]

    user_drop = lambda : [
        DROP_ITEM('{{$store.state.account.name}}', disabled=''),
        DROP_DIVIDER(),
        DROP_ITEM(UserView.entry_login(), to=Route.Account.login, v_show='!has_auth()'),
        DROP_ITEM(UserView.entry_logout(), to=Route.Account.logout, v_show='has_auth()'),
        DROP_ITEM(UserView.entry_update(), to=Route.Account.update, v_show='has_auth()'),
        DROP_ITEM(UserView.entry_register(), to=Route.Account.register, v_show='!has_auth()'),
        DROP_ITEM(UserView.entry_manager(), to=Route.Admin.accounts,),
    ]

    right_list = lambda : [
        NAV_FORM(ArkonNav.form_body()),
        NAV_ITEM_DROP(ArkonNav.lang_drop(), text="Lang", right=''),
        NAV_ITEM_DROP(ArkonNav.user_drop(), text="User", right=''),
    ]

    main_body = lambda : [
        NAVBAR_NAV(ArkonNav.left_list()),
        NAVBAR_NAV(ArkonNav.right_list(), cls="ml-auto"),
    ]

    main_id = 'main-nav-bar'

    main_bar = lambda : NAVBAR([
        NAVBAR_BRAND(FONT_ICON(
            icon='heartbeat', v_bind_transform='transform_brand_icon',
        )),
        NAVBAR_TOGGLE(target=ArkonNav.main_id),
        COLLAPSE(ArkonNav.main_body(), id=ArkonNav.main_id, is_nav=''),
    ], toggleable="lg", type="dark", variant="info")


class StateFun:

    @staticmethod
    def increment(state, *_) -> None:
        print("increment")
        state.count += 1

    @staticmethod
    def decrement(state, *_) -> None:
        print("decrement")
        state.count -= 1

    @staticmethod
    def with_account(state, account:dict) -> None:
        state.account = account


class ArkonFun:

    @staticmethod
    def router_move_back():
        print(f"router_move_back")
        router = this['$router']
        if window.history.size > 1:
            router.go(-1)
        else:
            router.push(Route.home)

    @staticmethod
    def perform_context_fetch(*_):
        router = this['$router']
        print(f"perform_context_fetch: {router}")

    @staticmethod
    def method_list(bucket:type) -> list:
        method_list = list()
        for intent in dir(bucket):
            if intent.startswith("_"):
                continue
            member = getattr(StateFun, intent)
            if callable(member):
                method_list.append((intent, member))
        return method_list


class GateFun:

    @staticmethod
    def policy_config():
        return new_dict(
        )


class ArkonView:

    Home = new_dict(template='<p>home page</p>')
    About = new_dict(template=DualListUnit.tag().outerHTML)
    UserLogin = new_dict(template=UserLoginUnit.tag().outerHTML)
    UserLogout = new_dict(template=UserLogoutUnit.tag().outerHTML)
    UserUpdate = new_dict(template=UserUpdateUnit.tag().outerHTML)
    UserRegister = new_dict(template=UserRegisterUnit.tag().outerHTML)
    AdminAccounts = new_dict(template=DualListUnit.tag().outerHTML)

#     view = TRANSITION(ROUTER_VIEW(), name="fade")
#     view = ROUTER_VIEW(**{"v-bind:key" : "$route.fullPath"})

    def __init__(self):

        view = ROUTER_VIEW()

        root = CONTAINER()
        root.appendChild(ArkonNav.main_bar())
        root.appendChild(view)

        arkon = document.getElementById('arkon')
        arkon.appendChild(root)

        self.arkon = arkon

#         root.appendChild(BUTTON('INC {{this.$store.state.count}}', v_on_click='increment'))
#         root.appendChild(BUTTON('DEC {{this.$store.state.count}}', v_on_click='decrement'))

#         root.appendChild(BUTTON('INC {{this.$store.state.count}}', v_on_click=name_of_fun(StateFun.increment)))
#         root.appendChild(BUTTON('DEC {{this.$store.state.count}}', v_on_click=name_of_fun(StateFun.decrement)))

#     root <= CounterUnit.tag('', title='Count 1')
#     root <= CounterUnit.tag('', title='Count 2')
#     root <= CounterUnit.tag('', title='Count 3')


class ArkonUnit(StateFun):

    class Invoker:

        def __init__(self, unit, intent, method):
            self.unit = unit
            self.intent = intent
            self.method = method

        def invoke_action(self, context, *args):
            context.commit(self.intent, *args)

        def invoke_mutation(self, state, *args):
            self.method(state, *args)

        def invoke_method(self, *args):
            self.unit.store.dispatch(self.intent, *args)

    def __init__(self):

        self.timers = new_dict(
            timer_check_auth=new_dict(time=3000, autostart=True, repeat=True),
        )

        actions = new_dict()
        mutations = new_dict()
        methods = new_dict(
            has_auth=self.has_auth,
            router_move_back=self.router_move_back,
            perform_context_fetch=self.perform_context_fetch,
            timer_check_auth=self.timer_check_auth,
        )
        computed = new_dict(
            transform_brand_icon=self.transform_brand_icon,
        )

        def verify_intent(intent):
            assert(not intent in actions)
            assert(not intent in mutations)
            assert(not intent in methods)

        for intent, method in ArkonFun.method_list(StateFun):
            verify_intent(intent)
            invoker = ArkonUnit.Invoker(self, intent, method)
            actions[intent] = invoker.invoke_action
            mutations[intent] = invoker.invoke_mutation
            methods[intent] = invoker.invoke_method

        self.route_list = [
            new_dict(path=Route.root, redirect=Route.home),
            new_dict(path=Route.home, component=ArkonView.Home, meta=new_dict(need_auth=True)),
            new_dict(path=Route.about, component=ArkonView.About, meta=new_dict(need_auth=True)),
            new_dict(path=Route.Account.login, component=ArkonView.UserLogin),
            new_dict(path=Route.Account.logout, component=ArkonView.UserLogout),
            new_dict(path=Route.Account.update, component=ArkonView.UserUpdate),
            new_dict(path=Route.Account.register, component=ArkonView.UserRegister),
            new_dict(path=Route.Admin.accounts, component=ArkonView.AdminAccounts),
        ]

        self.auth = window.VueAuthenticate.factory(window.Vue.prototype['$http'], new_dict(
            storageType='localStorage',
            storageNamespace='healer.auth',
            tokenPrefix=None,
            tokenName='token',
            loginUrl='/auth/login',
            logoutUrl='/auth/logout',
            updateUrl='/auth/update',
            refreshUrl='/auth/refresh',
            registerUrl='/auth/register',
        ))

        self.gate = newVueGate(new_dict(
            auth=self.user_account,
            policies=GateFun.policy_config(),
        ))

        self.persist = newVuexPersistence(new_dict(
            key='healer.vuex.store',
            storage=window.localStorage,
        ))

        self.store = newVuexStore(new_dict(
            strict=True,
            state=new_dict(
                count=0,
                account=UserFun.default_account(),
            ),
            getters=new_dict(
            ),
            actions=actions,
            mutations=mutations,
            plugins=[self.persist.plugin],
        ))

        self.router = newVueRouter(new_dict(
            routes=self.route_list,
        ))

        self.router.beforeEach(self.router_check_auth)

        self.arkon = newVue(new_dict(
            el='#arkon',
            data=new_dict(
            ),
            gate=self.gate,
            store=self.store,
            router=self.router,
            timers=self.timers,
            watch={
                '$route': 'perform_context_fetch',
            },
            methods=methods,
            computed=computed,
            mixins=[window.VueIdleMixin],
            idle_opts=new_dict(
                idle_time=15 * 1000,
                react_on_active=self.react_on_active,
                react_on_passive=self.react_on_passive,
            ),
        ))

        self.arkon['$auth'] = self.auth

    def user_account(self) -> dict:
        return self.store.state.account

    def has_auth(self) -> bool:
        return self.auth.isAuthenticated()

    def timer_check_auth(self):
        if not self.has_auth():
            current_path = self.router.currentRoute.path
            if current_path in (Route.Account.login, Route.Account.register):
                pass
            else:
                print(f"session expired: {newDate()}")
                self.arkon.with_account(UserFun.default_account())
                self.router.push(Route.Account.login)

    def router_check_auth(self, route_into, route_from, apply_next) -> None:
        meta = route_into['meta']
        need_auth = meta['need_auth']
        if need_auth:
            if self.has_auth():
                apply_next()
            else:
                apply_next(Route.Account.login)
        else:
            apply_next()

    def router_move_back(self) -> None:
        print(f"router_move_back")
        router = self.router
        if window.history.size > 1:
            router.go(-1)
        else:
            router.push(Route.home)

    def perform_context_fetch(self, *_) -> None:
        router = self.router
        print(f"perform_context_fetch: {router}")

    def react_on_active(self) -> None:
        print("react_on_active")

    def react_on_passive(self) -> None:
        print("react_on_passive")

    def transform_brand_icon(self) -> str:
        if self.store.state._idle_js.has_active:
            return 'grow-1'
        else:
            return 'shrink-3'
