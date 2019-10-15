from guillotina import configure

app_settings = {
    # provide custom application settings here...
}


def includeme(root):
    """
    custom application initialization here
    """
    configure.scan("guillotina_evolution.commands")
    configure.scan("guillotina_evolution.utility")
