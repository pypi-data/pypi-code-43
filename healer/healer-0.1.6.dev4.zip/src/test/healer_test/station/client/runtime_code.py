
# class VuexStorePlugin:
#
#     key = 'store-state'
#
#     @staticmethod
#     def setup(store):
#         return VuexStorePlugin(store)
#
#     def __init__(self, store):
#         print("init")
#         self.configure(store)
#         store.subscribe(self.reactor)
#
#     def configure(self, store):
#         print("config")
#         state = window.localStorage.getItem(VuexStorePlugin.key)
#         console_log(state)
#         if state:
#             store.replaceState(JSON.parse(state));
#
#     def reactor(self, mutation, state):
#         print(f"reactor {state.to_dict()}")
#         action = mutation.type
#         console_log(action, state)
#         window.localStorage.setItem(VuexStorePlugin.key, JSON.stringify(state));