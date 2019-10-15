from cloudcix.client import Client


class AppManager:
    """
    The App Manager Application is a software system that manages CloudCIX Apps

    It allows Users to select and use apps, and allows Administrators to select which apps to deploy and give
    permissions to other Users.
    """
    _application_name = 'AppManager'

    app = Client(
        _application_name,
        'App/',
    )
    app_member = Client(
        _application_name,
        'App/{app_id}/Member/',
    )
    app_menu = Client(
        _application_name,
        'App/{app_id}/MenuItem/',
    )
    menu_item_user = Client(
        _application_name,
        'MenuItem/User/{user_id}/',
    )
