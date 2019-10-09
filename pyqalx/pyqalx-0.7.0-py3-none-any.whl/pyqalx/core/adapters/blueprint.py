from pyqalx.core.adapters.adapter import QalxNamedEntityAdapter
from pyqalx.core.entities.blueprint import Blueprint
from pyqalx.core.errors import QalxInvalidBlueprintError


class QalxBlueprint(QalxNamedEntityAdapter):
    _entity_class = Blueprint

    def _check_schema(self, schema):
        self._entity_class({}).check_schema(schema)

    def add(self, name, schema, meta=None, **kwargs):
        """
        Adds a QalxBlueprint with a valid `jsonschema` `schema`.
        If the `schema` is invalid then a `jsonschema.SchemaError` is raised

        :param name: The name of this blueprint
        :type name: str
        :param schema: The schema that you want to set on the Blueprint.
        :type schema: dict
        :param meta: A dictionary of metadata to store
        :type meta: dict

        :return: pyqalx.core.entities.Blueprint
        :raises: jsonschema.SchemaError
        """
        self._check_schema(schema)
        entity_type = schema.get('entity_type', None)
        if entity_type is None:
            raise QalxInvalidBlueprintError('schema must specify '
                                            '`entity_type` top level key which'
                                            'has a valid `entity_type` as the'
                                            'value')
        return super(QalxBlueprint, self).add(name=name,
                                              schema=schema,
                                              entity_type=entity_type,
                                              meta=meta,
                                              **kwargs)

    def save(self, entity, **kwargs):
        """
        Saves any updates to the given Blueprint.  Validates that the `schema`
        on the entity is a valid `jsonschema` schema


        :param entity: A valid pyqalx.core.entities.Blueprint instance
        :param kwargs: Any kwargs you want to save against this `Blueprint`
        :return: pyqalx.core.entities.Blueprint
        :raises: jsonschema.SchemaError
        """
        self._check_schema(entity['schema'])
        return super(QalxBlueprint, self).save(entity=entity,
                                               **kwargs)


