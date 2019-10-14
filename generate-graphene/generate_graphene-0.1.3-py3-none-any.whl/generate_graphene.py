from typing import Type
from django.db.models import Model
from graphene import ObjectType
from graphene_django_extras import DjangoObjectType, DjangoSerializerMutation
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from typedecorator import Nullable

from generate_graphene.config import DEFAULT_FILTERS_FIELDS
from generate_graphene.utils import (
    get_model_name,
    AbstractModelSerializerMutation,
    AuthDjangoFilterListField,
    AuthDjangoObjectField,
    set_optionally)


class GenerateGraphene:
    def __init__(self):
        self._object_types = dict()
        self._model_serializers = dict()
        self._model_mutations = dict()
        self._model_excluded_fields = dict()
        self._models_to_register = list()

    _object_types = None
    _model_serializers = None
    _model_mutations = None
    _model_excluded_fields = None
    _models_to_register = None

    def exclude_single_field(self, m: Type[Model]) -> Type[Model]:
        """
        Query wont include a field to query a single instance for the passed model
        """
        self._exclude_field(m, "single")
        return m

    def exclude_list_field(self, m: Type[Model]) -> Type[Model]:
        """
        Query wont include a field to query a list for the passed model
        """
        self._exclude_field(m, "list")
        return m

    def exclude_create_field(self, m: Type[Model]) -> Type[Model]:
        """
        Mutations wont include a field to create an instance
        """
        self._exclude_field(m, "create")
        return m

    def exclude_update_field(self, m: Type[Model]) -> Type[Model]:
        """
        Mutations wont include a field to update an instance
        """
        self._exclude_field(m, "update")
        return m

    def exclude_delete_field(self, m: Type[Model]) -> Type[Model]:
        """
        Mutations wont include a field to delete an instance
        """
        self._exclude_field(m, "delete")
        return m

    def register_model(self, m: Type[Model]) -> Type[Model]:
        """
        DjangoObjectType and ModelSerializer will be generated for this model,
        unless these are already manually created and registered to this class.

        By default all operations will be possible:
            - Query single instance
            - Query list of instances
            - Create mutation
            - Read mutation
            - Update mutation
        """
        if not issubclass(m, Model):
            raise Exception('Expected subclass of "Model", got {}'.format(m))

        self._models_to_register.append(m)
        return m

    def set_mutation(
        self, model_mutation: Type[DjangoSerializerMutation]
    ) -> Type[DjangoSerializerMutation]:
        """
        Passed DjangoSerializerMutation will be used when creating graphene mutation fields.

        By default the following operations will be possible:
            - Create mutation
            - Read mutation
            - Update mutation
        """
        model = getattr(model_mutation._meta, "model")
        model_name = get_model_name(model)

        if model_name in self._model_mutations:
            raise Exception(
                "model_serializers already contains a serializer for {}".format(
                    model_name
                )
            )

        if not issubclass(model_mutation, DjangoSerializerMutation):
            raise Exception(
                'Expected subclass of "DjangoSerializerMutation", got {}'.format(
                    model_mutation
                )
            )

        self._model_mutations[model_name] = model_mutation
        return model_mutation

    def register_serializer(
        self, model_serializer: Type[ModelSerializer]
    ) -> Type[ModelSerializer]:
        """
        Passed ModelSerializer will be used when creating DjangoSerializerMutation.
        You will still have to call 'register_serializer' or 'register_model' to create mutation fields
        """
        model = getattr(model_serializer.Meta, "model")
        model_name = get_model_name(model)

        if model_name in self._model_serializers:
            raise Exception(
                "model_serializers already contains a serializer for {}".format(
                    model_name
                )
            )

        if not issubclass(model_serializer, ModelSerializer):
            raise Exception(
                'Expected subclass of "ModelSerializer", got {}'.format(
                    model_serializer
                )
            )

        self._model_serializers[model_name] = model_serializer
        return model_serializer

    def register_object_type(
        self, object_type: Type[DjangoObjectType]
    ) -> Type[DjangoObjectType]:
        """
        By default the following operations will be possible:
            - Query single instance
            - Query list of instances
        """
        if not issubclass(object_type, DjangoObjectType):
            raise Exception(
                'Expected subclass of "DjangoObjectType", got {}'.format(object_type)
            )

        model = object_type._meta.model
        self._object_types[get_model_name(model)] = object_type
        return object_type

    def get_object_type(self, m: Type[Model]) -> Type[DjangoObjectType]:
        self._create_object_type(m)
        return self._object_types[get_model_name(m)]

    def get_model_serializer(self, m: Type[Model]) -> Type[ModelSerializer]:
        self._create_model_serializer(m)
        return self._model_serializers[get_model_name(m)]

    def get_mutation_class(self, m: Type[Model]) -> Type[DjangoSerializerMutation]:
        self._create_mutation_class(m)
        return self._model_mutations[get_model_name(m)]

    def register_graphql_objects(
        self,
        input_query: Nullable(Type[ObjectType]),
        input_mutations: Nullable(Type[ObjectType]),
    ) -> [Type[ObjectType], Type[ObjectType]]:
        # copy input so we dont change original query/mutations
        class CopiedQuery(input_query, ObjectType):
            pass

        class CopiedMutations(input_mutations, ObjectType):
            pass

        for model in self._models_to_register:
            # Create object types for registered models,
            # if they dont already exist
            self._create_object_type(model)
            self._create_mutation_class(model)

        for model_name, object_type in self._object_types.items():
            if model_name in self._model_excluded_fields:
                excluded_fields = self._model_excluded_fields[model_name]
            else:
                excluded_fields = []

            # Create instance and list fields, if they dont exist and are not excluded
            if "single" not in excluded_fields:
                field_name = model_name
                set_optionally(
                    CopiedQuery, field_name, AuthDjangoObjectField(object_type)
                )

            if "list" not in excluded_fields:
                field_list_name = "{}s".format(model_name)
                set_optionally(
                    CopiedQuery, field_list_name, AuthDjangoFilterListField(object_type)
                )

        for model_name, mutation_class in self._model_mutations.items():
            if model_name in self._model_excluded_fields:
                excluded_fields = self._model_excluded_fields[model_name]
            else:
                excluded_fields = []

            # Create create/delete/update fields, if they dont exist and are not excluded
            if "create" not in excluded_fields:
                create_name = "create_{}".format(model_name)
                set_optionally(
                    CopiedMutations, create_name, mutation_class.CreateField()
                )

            if "update" not in excluded_fields:
                update_name = "update_{}".format(model_name)
                set_optionally(
                    CopiedMutations, update_name, mutation_class.UpdateField()
                )

            if "delete" not in excluded_fields:
                delete_name = "delete_{}".format(model_name)
                set_optionally(
                    CopiedMutations, delete_name, mutation_class.DeleteField()
                )

        # recompose into ObjectType
        class Query(CopiedQuery, ObjectType):
            pass

        class Mutations(CopiedMutations, ObjectType):
            pass

        return Query, Mutations

    def _exclude_field(self, m: Type[Model], field_name: str):
        model_name = get_model_name(m)

        if not model_name in self._model_excluded_fields:
            self._model_excluded_fields[model_name] = list()

        self._model_excluded_fields[model_name].append(field_name)

    def _create_model_serializer(self, m: Type[Model]):
        model_name = get_model_name(m)

        if model_name in self._model_serializers:
            return

        class ModelSerializer(serializers.ModelSerializer):
            class Meta:
                name = model_name
                model = m
                exclude = []

        self._model_serializers[model_name] = ModelSerializer

    def _create_mutation_class(self, m: Type[Model]):
        model_name = get_model_name(m)

        if model_name in self._model_mutations:
            return

        class ModelSerializerMutation(AbstractModelSerializerMutation):
            class Meta:
                name = "{}Mutation".format(model_name)
                input_field_name = "{}Input".format(model_name)
                serializer_class = self.get_model_serializer(m)

        self._model_mutations[model_name] = ModelSerializerMutation

    def _create_object_type(self, m: Type[Model]):
        model_name = get_model_name(m)

        if model_name in self._object_types:
            return

        class DjangoObjectTypeSubclass(DjangoObjectType):
            class Meta:
                filter_fields = DEFAULT_FILTERS_FIELDS
                name = f"{model_name[0].upper()}{model_name[1:]}Type"
                model = m

        self._object_types[model_name] = DjangoObjectTypeSubclass
