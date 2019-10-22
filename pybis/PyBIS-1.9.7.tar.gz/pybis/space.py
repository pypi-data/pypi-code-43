from .attribute import AttrHolder
from .openbis_object import OpenBisObject 
from .utils import parse_jackson, check_datatype, split_identifier, format_timestamp, is_identifier, is_permid, nvl, VERBOSE


class Space(
    OpenBisObject,
    entity='space',
    single_item_method_name='get_space'
):
    """ managing openBIS spaces
    """

    def __dir__(self):
        """all the available methods and attributes that should be displayed
        when using the autocompletion feature (TAB) in Jupyter
        """
        return [
            'get_projects()', 
            "new_project()", 
            'get_samples()', 
            'delete()'
        ] + super().__dir__()

    def __str__(self):
        return self.data.get('code', None)

    def get_samples(self, **kwargs):
        return self.openbis.get_samples(space=self.code, **kwargs)

    get_objects = get_samples  # Alias

    def get_sample(self, sample_code, project_code=None):
        if is_identifier(sample_code) or is_permid(sample_code):
            return self.openbis.get_sample(sample_code)
        else:
            if project_code is None:
                return self.openbis.get_sample('/{}/{}'.format(self.code,sample_code) )
            else:
                return self.openbis.get_sample('/{}/{}/{}'.format(self.code, project_code, sample_code) )
    get_object = get_sample  # Alias


    def get_projects(self, **kwargs):
        return self.openbis.get_projects(space=self.code, **kwargs)

    def new_project(self, code, description=None, **kwargs):
        return self.openbis.new_project(self.code, code, description, **kwargs)

    def new_sample(self, **kwargs):
        return self.openbis.new_sample(space=self, **kwargs)


