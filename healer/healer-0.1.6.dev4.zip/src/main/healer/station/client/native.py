"""
Native javascript object setup
"""

from .assist import *


# __pragma__ ('skip')
def __new__(): pass
# __pragma__ ('noskip')


newDate = lambda : __new__(window.Date())
newObject = lambda : __new__(window.Object())

newVue = lambda *args : __new__(window.Vue(*args))
newVueGate = lambda *args : __new__(window.VueGate(*args))
newVueRouter = lambda *args : __new__(window.VueRouter(*args))
newVuexStore = lambda *args : __new__(window.Vuex.Store(*args))
newVuexPersistence = lambda *args : __new__(window.VuexPersistence(*args))

# __pragma__ ('noalias')
# __pragma__ ('alias', 'items', 'py_items')


# __pragma__ ('kwargs')
def new_dict(**kwargs):
    entry = newObject()
    for key, value in kwargs.items():
        entry[key] = value
    return entry
# __pragma__ ('nokwargs')

#
#
#


window.Vue.config.productionTip = False

window.Vue.use(window.VueRouter)

window.Vue.use(window.BootstrapVue)

window.Vue.use(window.VueGate)

window.Vue.use(window.VueTimers)

window.Vue.use(window.VueAxios, window.axios)

window.Vue.use(window.VeeValidate, new_dict(
    inject=True,
    errorBagName='validate_error',
    fieldsBagName='validate_field',
))

#
#
#

window.Vue.component("draggable", window.VueDraggable)

window.Vue.component('font-awesome-icon', window.FontAwesomeIcon)
