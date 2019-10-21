from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet

from orionframework.media.settings import Document, Image
from orionframework.utils.models import set_attrs


class ServiceMedia(object):
    """
    Service used to manage the lifecycle of the media models.
    """

    category = 0
    """
    The category in which the image is saved against
    """

    model_class = None
    """
    The underlying model class being managed by this service.
    """

    parent_class = None
    """
    The parent related class we are contributing to.
    """

    parent = None
    """
    The parent model related to the maintained images
    """

    def __init__(self, category=0, parent=None, parent_class=None, **kwargs):

        super(ServiceMedia, self).__init__(**kwargs)

        self.category = category
        self.parent = parent
        self.parent_class = parent_class

        if not self.parent_class and self.parent:
            self.parent_class = self.parent.__class__

    def __iter__(self):
        return self.filter().__iter__()

    def get_parent_type(self):

        if not hasattr(self, "_parent_type"):
            self._parent_type = ContentType.objects.get_for_model(self.parent_class)

        return self._parent_type

    def delete(self, **kwargs):

        self.filter(**kwargs).delete()

    def all(self):
        return self.filter()

    def filter(self, **kwargs):

        if self.category:
            kwargs["category"] = self.category

        if self.parent_class:
            kwargs["parent_type"] = self.get_parent_type()

        if self.parent and self.parent.id:
            kwargs["parent_id"] = self.parent.id

        return self.model_class.objects.filter(**kwargs).indexed().select_related("created_by", "modified_by")

    def create(self, file, category=None, **kwargs):

        model = self.model_class(file=file,
                                 category=category or self.category,
                                 **kwargs)

        if self.parent_class:
            model.parent_type = self.get_parent_type()

        if self.parent and self.parent.id:
            model.parent_id = self.parent.id

        model.save()

        return model

    def update(self, model, **kwargs):

        if kwargs.get("tags"):
            model.tags.set(*kwargs.pop("tags"), clear=True)

        set_attrs(model, kwargs)

        model.save()

        return model


class ServiceImage(ServiceMedia):
    """
    Service used to manage the lifecycle of the Image model.
    """

    model_class = Image


class ServiceDocument(ServiceMedia):
    """
    Service used to manage the lifecycle of the Document model.
    """

    model_class = Document
