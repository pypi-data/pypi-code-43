
from django.db.models.fields.related import ManyToManyField
from django.db.models import FieldDoesNotExist

__all__ = [
    'RepresentationMixin'
]


class RepresentationMixin:
    related_representations = {}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        model_meta = self.Meta.model._meta
        for field_name, serializer_class in self.related_representations.items():
            data[field_name] = None
            related_instance = None
            many = False

            try:
                field = model_meta.get_field(field_name)
                if isinstance(field, (ManyToManyField,)):
                    related_instance = getattr(instance, field_name).all()
                    many = True
            except FieldDoesNotExist:
                pass

            if related_instance is None:
                related_instance = getattr(instance, field_name)

            if related_instance is not None:
                data[field_name] = serializer_class(instance=related_instance, context=self.context, many=many).data
        return data
