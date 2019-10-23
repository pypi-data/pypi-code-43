# Imports from Django.
from django.db import models


# Imports from civic_utils.
from civic_utils.models.helpers import extract_nested_key
from civic_utils.models.querysets import BaseNaturalKeyQuerySet
from civic_utils.models.querysets import CivicBaseQuerySet


class CivicBaseManager(models.Manager):
    """"""

    def get_queryset(self):
        return CivicBaseQuerySet(self.model, using=self._db)


class NaturalKeyManagerMixin(object):
    """A mixin to add default natural-key behaviors to Civic managers.

    Borrows somewhat heavily from the following project:
    https://github.com/wq/django-natural-keys/
    """

    def get_queryset(self):
        return BaseNaturalKeyQuerySet(self.model, using=self._db)

    def natural_key_kwargs(self, *args):
        """Turn args >> kwargs by merging with the natural key fields.

        Falls through to the method with the same name on the QuerySet.
        """
        return self.get_queryset().natural_key_kwargs(*args)

    def get_by_natural_key(self, *args):
        """Return the object corresponding to the provided natural key.

        (Generic implementation of the standard Django function).
        """
        natural_kwargs = self.natural_key_kwargs(*args)

        # Since kwargs already has __ lookups in it, we could just do this:
        # return self.get(**natural_kwargs)

        # But, we should call each related model's get_by_natural_key() method,
        # in case it's been overridden.
        for name, rel_to in self.model.get_natural_key_info():
            if not rel_to:
                continue

            # Extract natural key for related object
            nested_key = extract_nested_key(natural_kwargs, rel_to, name)
            if nested_key:
                # Update natural_kwargs with related object
                try:
                    natural_kwargs[name] = rel_to.objects.get_by_natural_key(
                        *nested_key
                    )
                except rel_to.DoesNotExist:
                    # If related object doesn't exist, assume the model we're
                    # querying for doesn't exist, either.
                    raise self.model.DoesNotExist()
            else:
                natural_kwargs[name] = None

        return self.get(**natural_kwargs)


class BaseNaturalKeyManager(NaturalKeyManagerMixin, models.Manager):
    pass
