from djangopost.models import CategoryModel


def dpCategoryUniversalContext(request):
    djangopost_category = CategoryModel.objects.filter_publish()
    return {"djangopost_category": djangopost_category}
