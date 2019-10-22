from .property import PropertyHolder
from .attribute import AttrHolder
from .utils import VERBOSE
from .definitions import get_definition_for_entity

class OpenBisObject():

    def __init_subclass__(
        cls,
        entity=None,
        single_item_method_name=None
    ):
        """create a specialized parent class.
        The class that inherits from OpenBisObject does not need
        to implement its own __init__ method in order to provide the
        entity name. Instead, it can pass the entity name as a param:
        class XYZ(OpenBisObject, entity="myEntity")
        """
        cls._entity=entity
        cls._single_item_method_name=single_item_method_name

    def __init__(self, openbis_obj, type=None, data=None, props=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['type'] = type
        self.__dict__['p'] = PropertyHolder(openbis_obj, type)
        self.__dict__['a'] = AttrHolder(openbis_obj, self._entity, type)

        # existing OpenBIS object
        if data is not None:
            self._set_data(data)

        if props is not None:
            for key in props:
                setattr(self.p, key, props[key])

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])


    def __dir__(self):
        defs = get_definition_for_entity(self.entity)
        if self.is_new:
            return defs['attrs_new']
        else:
            return list(set(defs['attrs'] + defs['attrs_up']))


    def _set_data(self, data):
        # assign the attribute data to self.a by calling it
        # (invoking the AttrHolder.__call__ function)
        self.a(data)
        self.__dict__['data'] = data

        # put the properties in the self.p namespace (without checking them)
        if 'properties' in data:
            for key, value in data['properties'].items():
                self.p.__dict__[key.lower()] = value
            
        # object is already saved to openBIS, so it is not new anymore
        self.a.__dict__['_is_new'] = False

    @property
    def attrs(self):
        return self.__dict__['a']

    @property
    def space(self):
        try:
            return self.openbis.get_space(self._space['permId'])
        except Exception:
            pass

    @property
    def project(self):
        try:
            return self.openbis.get_project(self._project['identifier'])
        except Exception:
            pass

    @property
    def experiment(self):
        try:
            return self.openbis.get_experiment(self._experiment['identifier'])
        except Exception:
            pass
    collection = experiment  # Alias

    @property
    def sample(self):
        try:
            return self.openbis.get_sample(self._sample['identifier'])
        except Exception:
            pass
    object = sample # Alias

    @property
    def _permId(self):
        try:
            return self.data['permId']
        except Exception:
            return ""

    @property
    def permId(self):
        try:
            return self.data['permId']['permId']
        except Exception:
            return ""
        

    def __getattr__(self, name):
        return getattr(self.__dict__['a'], name)

    def __setattr__(self, name, value):
        if name in ['set_properties', 'set_tags', 'add_tags']:
            raise ValueError("These are methods which should not be overwritten")
        setattr(self.__dict__['a'], name, value)

    def _repr_html_(self):
        """Print all the assigned attributes (identifier, tags, etc.) in a nicely formatted table. See
        AttributeHolder class.
        """
        return self.a._repr_html_()

    def __repr__(self):
        """same thing as _repr_html_() but for IPython
        """
        return self.a.__repr__()


    def delete(self, reason):
        """Delete this openbis entity.
        A reason is mandatory to delete any entity.
        """
        if not self.data:
            return
 
        self.openbis.delete_openbis_entity(
            entity=self._entity,
            objectId=self.data['permId'],
            reason=reason
        )
        if VERBOSE: print(
            "{} {} successfully deleted.".format(
                self._entity,
                self.permId
            )
        )

    def _get_single_item_method(self):
        single_item_method = None
        if self._single_item_method_name:
            single_item_method = getattr(
                self.openbis, self._single_item_method_name
            )
        else:
            # try to guess the method...
            single_item_method = getattr(self.openbis, 'get_' + self.entity)

        return single_item_method


    def save(self):
        get_single_item = self._get_single_item_method()
        # check for mandatory properties before saving the object
        props = None
        if self.props:
            for prop_name, prop in self.props._property_names.items():
                if prop['mandatory']:
                    if getattr(self.props, prop_name) is None \
                    or getattr(self.props, prop_name) == "":
                        raise ValueError(
                            "Property '{}' is mandatory and must not be None".format(prop_name)
                        )

            props = self.p._all_props()

        # NEW
        if self.is_new:
            request = self._new_attrs()
            if props: request["params"][1][0]["properties"] = props

            resp = self.openbis._post_request(self.openbis.as_v3, request)

            if VERBOSE: print("{} successfully created.".format(self.entity))
            new_entity_data = get_single_item(resp[0]['permId'], only_data=True)
            self._set_data(new_entity_data)
            return self

        # UPDATE
        else:
            request = self._up_attrs(method_name=None, permId=self._permId)
            if props: request["params"][1][0]["properties"] = props

            resp = self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("{} successfully updated.".format(self.entity))
            new_entity_data = get_single_item(self.permId, only_data=True)
            self._set_data(new_entity_data)

