"""stub to avoid import errors"""


class webworker:

    current_worker = None

    class Message:
        ""

    class WorkerChild:

        def exec(self):""

        def bind_message(self): ""

        def post_reply(self): ""

    class WorkerParent:

        def post_message(self): ""


class NEW:

    @classmethod
    def new(cls, *args, **kwargs):
        ...


def load(path):
    ...


def bind(target, ev):
    ...


class html:
    ""

    HR = object
    BR = object
    DIV = object
    SPAN = object

    def maketag(self):
        ...


class local_storage:

    storage = dict()


class document:
    ""

    @staticmethod
    def getElementById(): ""


class window:

    String = str

    Number = int

    Object = object

    Boolean = bool

    __BRYTHON__ = None

    QUnit = None

    class history:
        length = ''

    @staticmethod
    def bind(el, ev): ""

    @staticmethod
    def setTimeout(func, delay): ""

    @staticmethod
    def clearTimeout(timer_id): ""

    class localStorage:

        @staticmethod
        def getItem(): ""

        @staticmethod
        def setItem(): ""

    class console:

        @staticmethod
        def log(): ""

    class location:
        hash = ''
        href = ''
        origin = ''
        protocol = ''
        host = ''

    class Array:

        @classmethod
        def isArray(cls, obj):
            ...

    class Vuex:

        class Store(NEW): ""

    class Vue(NEW):

        @classmethod
        def component(cls, name, opts=None):
            ...

        @classmethod
        def set(cls, obj, key, value):
            ...

        @classmethod
        def delete(cls, obj, key):
            ...

        @classmethod
        def use(cls, plugin, *args, **kwargs):
            ...

        @classmethod
        def directive(cls, name, directive=None):
            ...

        @classmethod
        def filter(cls, name, method):
            ...

        @classmethod
        def mixin(cls, mixin):
            ...

    class VueTimers(NEW): ""

    class VueRouter(NEW): ""

    class BootstrapVue(NEW): ""

    class bootstrapVue(NEW): ""

    class VueAuthPlugin(NEW) : ""

    class axios (NEW): ""

    class VueAxios (NEW): ""

    class VueAuthenticate(NEW): ""

    class VueGate(NEW): ""

    class VeeValidate(NEW): ""

    class VuexPersistence(NEW): ""

    class VueDraggable(NEW): ""

    class FontAwesomeIcon(NEW): ""

    class IdleVue: ""

    class VueIdleMixin: ""


class timer:

    @staticmethod
    def set_interval(func, interval): ""

    @staticmethod
    def set_timeout(func, delay): ""


class ajax:

    class ajax:

        def open(self, method, url, async):
            ...

        def bind(self, ev, method):
            ...

        def send(self):
            ...
