from functools import wraps
from typing import Type, Any, Dict

from django.db.models import Model
from graphene_django_extras import (
    DjangoFilterListField,
    DjangoSerializerMutation,
    DjangoObjectField,
)

from graphene_django_extras.utils import get_Object_or_None
from graphql import GraphQLError
from typedecorator import Nullable

ModelNameType = str
DEFAULT_HAS_PERMISSIONS = False


class UserError(GraphQLError):
    pass


def set_optionally(obj: object, name: str, value: any):
    if not hasattr(obj, name):
        setattr(obj, name, value)


def authenticated_resolver(resolver: callable):
    """
    Wrap graphene resolver to raise exception if user is not logged in
    """

    @wraps(resolver)
    def _impl(self, info, *args, **kwargs):
        user = info.context.user
        if user and user.is_authenticated:
            return resolver(self, info, *args, **kwargs)

        raise UserError("Please login")

    return _impl


def get_model_name(model: Type[Model]) -> ModelNameType:
    return model.__name__[0].lower() + model.__name__[1:]


def get_id(user) -> Nullable(int):
    if not user:
        return None

    if user.is_authenticated:
        return user.id


def assert_permission(model_instance: Type[Model], user, operation: str):
    if not model_instance or not hasattr(model_instance, "has_permission"):
        return DEFAULT_HAS_PERMISSIONS

    if user and getattr(user, "is_superuser", False):
        return True

    no_permission = not model_instance.has_permission(get_id(user), operation)

    if (not user or not user.is_authenticated) and no_permission:
        raise UserError("Please login")

    if no_permission:
        raise UserError(f"User '{user.username}' has no permission.")


def has_permission(model_instance: Type[Model], user, operation: str) -> bool:
    """
    Check for the implementation of 'has_permission' method on model,
    which is as follows:

    def has_permission(self, user_id: int, operation: str) -> bool
        :param user_id: ID of user who made the query / mutation
        :param operation: One of "create", "read", "update", "delete"
        :return: does this user have permission to 'self' instance?
    """
    try:
        assert_permission(model_instance, user, operation)
        return True
    except GraphQLError:
        return False


class AuthDjangoFilterListField(DjangoFilterListField):
    def list_resolver(
        self, manager, filterset_class, filtering_args, root, info, **kwargs
    ):
        """
        Uses regular list_resolver to get all objects, but filters out all
        model instances that the user does not have permissions to.

        Not very efficient but very convenient.
        """
        unfiltered_models = DjangoFilterListField.list_resolver(
            manager, filterset_class, filtering_args, root, info, **kwargs
        )
        return list(
            filter(
                lambda obj: has_permission(obj, info.context.user, "read"),
                list(unfiltered_models),
            )
        )


class AuthDjangoObjectField(DjangoObjectField):
    def object_resolver(self, manager, root, info, **kwargs):
        id = kwargs.pop("id", None)
        try:
            obj = manager.get_queryset().get(pk=id)
            assert_permission(obj, info.context.user, "read")
            return obj
        except manager.model.DoesNotExist:
            return None


class AbstractModelSerializerMutation(DjangoSerializerMutation):
    class Meta:
        abstract = True

    method = None

    @staticmethod
    def get_obj(cls, **kwargs):
        data = kwargs.get(cls._meta.input_field_name)
        if data:
            id = data.get("id", None)
        else:
            id = kwargs.get("id", None)

        return get_Object_or_None(cls._meta.model, pk=id)

    @staticmethod
    def assert_permission(cls, info, operation: str, **kwargs):
        assert_permission(cls.get_obj(cls, **kwargs), info.context.user, operation)

    @classmethod
    def save(cls, serialized_obj, root, info, **kwargs):
        operation = cls.method or "create"

        is_success, obj_or_error = super(AbstractModelSerializerMutation, cls).save(
            serialized_obj, root, info, **kwargs
        )

        if not is_success:
            return is_success, obj_or_error

        try:
            assert_permission(obj_or_error, info.context.user, operation)
        except GraphQLError as e:
            if cls.method == "create":
                obj_or_error.delete()

            return False, e

        return is_success, obj_or_error

    @classmethod
    def delete(cls, root, info, **kwargs):
        cls.method = "delete"
        cls.assert_permission(cls, info, "delete", **kwargs)
        return super(AbstractModelSerializerMutation, cls).delete(root, info, **kwargs)

    @classmethod
    def update(cls, root, info, **kwargs):
        cls.method = "update"
        cls.assert_permission(cls, info, "update", **kwargs)
        return super(AbstractModelSerializerMutation, cls).update(root, info, **kwargs)
