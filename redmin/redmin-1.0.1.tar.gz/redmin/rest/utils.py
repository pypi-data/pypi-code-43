from redmin.utils import memorize


@memorize
def get_all_models():
    import django.apps
    from redmin.models import RedminModel
    return [model for model in django.apps.apps.get_models() if issubclass(model, RedminModel) and model.__module__.split(".")[0] != 'redmin']


@memorize
def get_all_model_map():
    return {model.__name__: model for model in get_all_models()}
