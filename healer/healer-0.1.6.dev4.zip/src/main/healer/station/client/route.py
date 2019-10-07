"""
"""

class Route:
    root = '/'
    home = '/home'
    about = '/about'

    class Admin:
        accounts = '/admin/accounts'

    class Account:
        login = '/account/login'
        logout = '/account/logout'
        update = '/account/update'
        register = '/account/register'
