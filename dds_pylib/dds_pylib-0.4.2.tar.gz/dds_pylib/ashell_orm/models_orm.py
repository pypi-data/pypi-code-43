'''
A-Shell orm models

History:
    08-07-2019 - 1.0.0 - Stephen Funkhouser
        - Created
'''
from __future__ import unicode_literals, print_function
from exceptions import Exception
from copy import deepcopy

from django.db import models
from dds_pylib.pyext.struct import Struct

from dds_pylib.ashell_orm import ash_fields

class AshNoKeyException(Exception):
    ''' exception '''


class AshFileStruct(Struct):
    ''' file structure '''
    record_size = 0  # not used yet
    fileio_define = ''  # defaults to the model name (i.e. FILEIO_ZONE)

class AshInxUnqBase(models.Index):
    ''' '''

    def __init__(self, *args, **kwargs):
        super(AshInxUnqBase, self).__init__(*args, **kwargs)
        # default to just fields
        self.ashell_fields = self.fields

    @property
    def ashell_name(self):
        ''' '''
        return self.name

    def get_ashell_fields(self):
        pass

class AshIndex(AshInxUnqBase):
    ''' '''

    # def __init__(self, *args, **kwargs):
    #     super(AshIndex, self).__init__(*args, **kwargs)


class AshUnique(AshInxUnqBase):
    ''' '''

    # def __init__(self, *args, **kwargs):
    #     super(AshUnique, self).__init__(*args, **kwargs)

class AshModel(models.Model):
    ''' add methods necessary for
    - composite key fields
    - ORM code generation
    '''

    def __init__(self, *args, **kwargs):
        super(AshModel, self).__init__(*args, **kwargs)

        # tells us whether or not to use '.key' by default in variable member name
        self.use_defstruct_key = True
        # primary_file = None
        self.primary_file = AshFileStruct()
        # if defined use for variable substitution; otherwise, the model name is used
        self.ash_var_prefix = ''
        # if True append $ to the end of string variables
        self.ash_var_string_dollar_sign = True
        # used internally for memoize
        self.__has_key = None
        # field types that aren't allowed to have default fields
        # self._no_default_field_types = ['AshFiller']
        self._no_default_field_types = []
        self.index_add_primary_keys()
        self.calculate_map_levels()

    def calculate_map_levels(self):
        ''' iterate non key fields and calculate map levels
        taking unformatted map statements into account
        '''
        uf = {} # key by field name, value field
        uf_map = {} # key by field name, value map level
        for f in self.fields_non_key_iter():
            if f.get_internal_type() == 'AshUnformattedMap' or f.unformatted_map:
                if f.unformatted_map:
                    # get map level of parent
                    uf_map[f.name] = uf_map[f.unformatted_map] + 1
                else:
                    uf_map[f.name] = 2 # default map level
                uf[f.name] = f
        for fname, f in uf.iteritems():
            f.ash_map_level = uf_map[fname]

    def fields_iter(self):
        ''' Django model field generator '''
        for f in self._meta.get_fields():
            yield f

    def get_field(self, field):
        for f in self.fields_iter():
            if f.name == field:
                return f

    def fields_default_iter(self):
        ''' iterate all fields with defaults (except key fields)
        '''
        for f in self.fields_iter():
            if not self.is_field_key(field=f) and f.has_default() \
                    and not f.get_internal_type() in self._no_default_field_types:
                yield f

    def fields_non_key_iter(self):
        ''' iterate all fields with that are not key fields
        '''
        for f in self.fields_iter():
            if not self.is_field_key(field=f):
                yield f

    def index_add_primary_keys(self):
        ''' add primary key fields to index to make unique '''
        for idx in self.index_iter():
            # reset ashell fields
            idx.ashell_fields = []
            for f in idx.fields:
                field = deepcopy(self.get_field(f))
                # note we have to make a deepcopy of the
                # field to modify it without modifying the
                # field associated with the model i.e.(field name)
                if field.get_internal_type() in ash_fields.ash_field_numeric_types:
                    save_field = ash_fields.AshString(max_length=None)
                    save_field.__dict__.update(deepcopy(field.__dict__))
                    try:
                        varlen = field.index_map_string_varlen
                    except AttributeError:
                        # default string string variable length large
                        # enough
                        varlen = 11
                    save_field.ash_var_type.ash_type = 's'
                    save_field.max_length = varlen
                    save_field.ash_var_type.bytes = varlen
                    if field.get_internal_type() in ash_fields.ash_field_float_types:
                        save_field.key_format = ash_fields.ASH_FORMAT_SPACES
                    else:
                        save_field.key_format = ash_fields.ASH_FORMAT_LZEROS
                else:
                    save_field = field
                    if not hasattr(save_field, 'key_format'):
                        setattr(save_field, 'key_format', ash_fields.ASH_FORMAT_SPACES)
                # get field from name
                idx.ashell_fields.append(save_field)
            if isinstance(idx, AshIndex):
                for key_field in self.key_field_iter():
                    kf = deepcopy(key_field)
                    # note we have to make a deepcopy of the
                    # field to modify it without modifying the
                    # field associated with the model i.e.(field name)
                    kf.name = 'pk_{}'.format(kf.name)
                    idx.ashell_fields.append(kf)

    def index_iter(self, index_only=False, unique_only=False):
        ''' iterate indexes
        '''
        for idx in self._meta.indexes:
            if index_only:
                if isinstance(idx, AshIndex):
                    yield idx
            elif unique_only:
                if isinstance(idx, AshUnique):
                    yield idx
            else:
                yield idx

    def index_field_iter(self, index):
        ''' iterate one index fields '''
        # if index in self._meta.indexes:
        for idx in self._meta.indexes:
            if idx == index:
                for field in idx.ashell_fields:
                    yield field

    def has_index(self):
        if self._meta.indexes:
            return True
        return False

    @property
    def get_primary_fileio_define(self):
        fd = ''
        if self.primary_file is None:
            fd = 'FILEIO_%ORM_MODEL_NAME_UPPER%'
        elif not self.primary_file.fileio_define:
            fd = 'FILEIO_%ORM_MODEL_NAME_UPPER%'
        else:
            fd = self.primary_file.fileio_define
        return fd

    def is_field_key(self, field, inc_compsite_key=True):
        ''' determine if field is a key field

        params:
            inc_compsite_key - True include linking 'cmpkey'
                               False don't include
        '''
        if self.has_key():
            if self.has_candidate_key():
                if self.is_ash_candidate_key_field(field):
                    return True
            elif self.has_composite_key():
                if self.is_ash_composite_key_member_field(field):
                    return True
                if inc_compsite_key:
                    if self.is_ash_composite_key_field(field):
                        return True
        return False

    def is_ash_candidate_key_field(self, f):
        ''' determine if field is an ashell candidate key field
        params:
            f - django model field
        '''
        if f.get_internal_type() == 'AshCandidateKeyField':
            return True
        return False

    def is_ash_composite_key_field(self, f):
        ''' determine if field is an ashell composite key field
        params:
            f - django model field
        '''
        if f.get_internal_type() == 'AshCompositeKeyField':
            return True
        return False

    def is_ash_composite_key_member_field(self, f):
        ''' determine if field is an ashell composite key field
        params:
            f - django model field
        '''
        if f.get_internal_type() == 'AshCompositeKeyMemberField':
            return True
        return False

    def has_key(self):
        ''' determine if Model has a key defined, agnostic to type '''
        if self.__has_key is None:
            if self.has_candidate_key():
                self.__has_key = True
            elif self.has_composite_key():
                self.__has_key = True
            else:
                self.__has_key = False
        return self.__has_key

    def has_candidate_key(self):
        ''' determine if model has a candidate key defined. used by has_key '''
        if self.is_ash_candidate_key_field(self._meta.pk):
            return True
        return False

    def has_composite_key(self):
        ''' determine if model has a composite key defined. used by has_key '''
        if self.is_ash_composite_key_field(self._meta.pk):
            return True
        return False

    def has_auto_key(self):
        ''' determine if model has an auto_key '''
        if self.has_key():
            if list(self.key_field_iter(only_auto_key=True)):
                return True
        return False

    def has_unique_key(self):
        ''' determine if composite key has a unique_key '''
        if self.has_composite_key():
            for key_field in self.key_field_iter():
                if key_field.unique_key:
                    return True
        return False

    def get_key_field(self):
        ''' get model key field agnostic to type '''
        if self.has_key():
            return self._meta.pk

    def __key_field_iter_helper(self):
        key_field = self.get_key_field()
        for member in key_field.members:
            field = self.get_field(field=member)
            if field.unique_key:
                return 'unique_key'
        # default to auto_key test if not unique_key
        return 'auto_key'

    def key_field_iter(self, inc_auto_key=True, only_auto_key=False):
        ''' iterator over key fields agnostic to composite/candidate keys
        params:
            inc_auto_key - False exclude auto_key=True or unique_key=True keys
                           (currently only applies to composite)
            only_auto_key - True only include auto_key=True
                            (overrides inc_auto_key=False)
                            (currently only applies to composite)
        returns:
            django model field
        '''
        if self.has_key():
            key_field = self.get_key_field()
            if self.has_candidate_key():
                if inc_auto_key:
                    yield self._meta.pk
            elif self.is_ash_composite_key_field(key_field):
                # -----------------------------------------
                # determine if auto or unique key attribute should be tested
                # -----------------------------------------
                inc_attr = 'auto_key'   # default to auto_key test if not unique_key
                for member in key_field.members:
                    field = self.get_field(field=member)
                    if field.unique_key:
                        inc_attr = 'unique_key'
                # -----------------------------------------
                # if composite key iterate the members
                # -----------------------------------------
                for member in key_field.members:
                    field = self.get_field(field=member)
                    if only_auto_key:
                        # purposely not testing unique_key
                        if field.auto_key:
                            yield field
                        else:
                            continue
                    elif inc_auto_key:
                        yield field
                    elif not getattr(field, inc_attr):
                        yield field
        else:
            raise AshNoKeyException('model has no key')

    def print_key_name(self):
        if self.has_key():
            key_field = self.get_key_field()
            print ('key_field: ', key_field)
            for member in self.key_field_iter():
                print ('type: {t} member: {m}'.format(
                    t=type(member),
                    m=member.name
                ))
        else:
            print('no key')

    def print_fields(self, columns=True, keys=True):
        def ln(ct):
            print ('{c}'.format(c='-' * ct))

        ln(80)
        if columns:
            ct = 0
            for f in self._meta.get_fields():
                ct += 1
                print ('field: {f} {t1}'.format(
                    f=f,
                    t1=f.get_internal_type(),
                ))
        else:
            ct = len([_ for _ in self._meta.get_fields()])
        print ('table=[{tbl}] app=[{a}] ct=[{ct}]'.format(
            tbl=self._meta.db_table, a=self._meta.app_label, ct=ct))
        print ('pk_name=[{pkn}] pk_col=[{pkc}]'.format(
            pkn=self._meta.pk.name, pkc=self._meta.pk.column))

        if keys:
            print('hck: ', self.has_composite_key())
            self.print_key_name()

        ln(80)

    class Meta:
        abstract = True
