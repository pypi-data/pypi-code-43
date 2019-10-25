'''
A-Shell orm fields

History:
    08-07-2019 - 1.0.0 - Stephen Funkhouser
        - Created
'''
from __future__ import unicode_literals, print_function
from exceptions import Exception

from django.core import checks
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AshMutuallyExclusiveOptionException(Exception):
    ''' exception '''


class AshTypeArrayNoDimensions(Exception):
    ''' exception '''


class AshCompositeKeyFieldAutoUniqueException(Exception):
    ''' composite fields can not be both auto and unique '''


class AshType(object):
    ''' A-Shell Types '''

    def __init__(self, ash_type, bytes, def_type='', array=False, dimension_str=''):
        ''' name/type/sizes are required

        when array=True bytes represents the element bytes not total
        '''
        self.ash_type = ash_type
        self.bytes = bytes
        self.def_type = def_type
        self.array = array
        if self.array and not dimension_str:
            raise AshTypeArrayNoDimensions(
                'array defined without dimension string')
        if self.array:
            self.dimensions = dimension_str
            # calculate total bytes used by the array
            dl = dimension_str.split(',')
            ary_elements = 1  # calculate number of elements in array
            for x in dl:
                ary_elements *= int(x)
            # multiple number of elements by size of one element for total bytes
            self.total_bytes = ary_elements * int(self.bytes)
        else:
            # total bytes is just the single element
            self.dimensions = ''
            self.total_bytes = self.bytes

    def is_array(self):
        if self.array:
            return True
        return False

    def is_def_type(self):
        if self.def_type:
            return True
        return False

    def __str__(self):
        if self.def_type:
            return self.def_type
        return '{t},{s}'.format(t=self.ash_type, s=self.bytes)


ash_field_string_types = [
    'AshString',
    'AshCompositeKeyMemberField',
    'AshCandidateKeyField',
]
ash_field_numeric_types = [
    'AshBinary1',
    'AshBinary2',
    'AshBinary3',
    'AshBinary4',
    'AshBinary6',
    'AshFloat4',
    'AshFloat6',
    'AshFloat8',
]

ash_field_float_types = [
    'AshFloat4',
    'AshFloat6',
    'AshFloat8',
]

ASH_DEFAULT_CALLBACK = '__callback__'


class AshFieldMixin(models.Field):
    ''' default mixin '''

    def __init__(self, callback=False, unformatted_map='', auto_default_add=False, auto_default_update=False, *args, **kwargs):
        '''
        params:
            callback - determines how the value is formatted for ISAM key
            unformatted_map - specify the parent unformatted map
        '''
        self.ash_var_type = AshType(ash_type='', bytes=0)
        # the default map level is 2 under DEFSTRUCTS.
        # This will be automatically adjusted for fields that have AshUnformattedMap ancestors
        self.ash_map_level = 2

        self.callback = callback
        self.unformatted_map = unformatted_map
        self.auto_default_add = auto_default_add
        self.auto_default_update = auto_default_update
        if callback:
            kwargs['default'] = ASH_DEFAULT_CALLBACK
        # allows comment to be added to all fields as a keyword argument
        self.comment = kwargs.pop('comment', '')
        super(AshFieldMixin, self).__init__(*args, **kwargs)

    def get_ash_map_level(self):
        return self.ash_map_level

    def is_var_type_array(self):
        ''' test if ashell type is an array '''
        if self.ash_var_type and self.ash_var_type.is_array():
            return True
        return False

    def get_var_array_dimensions(self):
        ''' get A-Shell variable array dimensions if field has any '''
        if self.is_var_type_array():
            return '({})'.format(self.ash_var_type.dimensions,)
        return ''

    def get_var_type(self):
        ''' get A-Shell variable type '''
        if self.ash_var_type:
            if self.ash_var_type.def_type:
                return self.ash_var_type.def_type
            elif self.ash_var_type.ash_type is None:
                return ''
            else:
                return self.ash_var_type.ash_type
        return ''

    def get_var_size(self, total=False):
        ''' get A-Shell variable size '''
        if self.ash_var_type:
            if self.ash_var_type.bytes is None:
                return ''
            elif total:
                return self.ash_var_type.total_bytes
            else:
                return self.ash_var_type.bytes
        return 0

    def get_comment(self):
        return self.comment

    def deconstruct(self):
        name, path, args, kwargs = super(AshFieldMixin, self).deconstruct()
        del kwargs['default']

    @property
    def has_auto_now_add(self):
        if hasattr(self, 'auto_now_add'):
            return True
        return False

    @property
    def is_auto_now_add(self):
        if self.has_auto_now_add:
            return self.auto_now_add
        return False

    @property
    def has_auto_default_add(self):
        if hasattr(self, 'auto_default_add'):
            return True
        return False

    @property
    def is_auto_default_add(self):
        if self.auto_default_add:
            return self.auto_default_add
        return False

    @property
    def has_auto_now(self):
        if hasattr(self, 'auto_now'):
            return True
        return False

    @property
    def is_auto_now(self):
        if self.has_auto_now:
            return self.auto_now
        return False

    @property
    def has_auto_default_update(self):
        if hasattr(self, 'auto_default_update'):
            return True
        return False

    @property
    def is_auto_default_update(self):
        if self.auto_default_update:
            return self.auto_default_update
        return False


class AshUnformattedMap(AshFieldMixin):
    empty_strings_allowed = False
    description = _('A-Shell Unformatted MAP')

    def __init__(self, *args, **kwargs):
        super(AshUnformattedMap, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(ash_type=None, bytes=None)

    def get_internal_type(self):
        return 'AshUnformattedMap'


class PositiveBigIntegerField(models.BigIntegerField):
    empty_strings_allowed = False
    description = _('Big (8 byte) positive integer')

    def db_type(self, connection):
        '''
        Returns MySQL-specific column data type. Make additional checks
        to support other backends.
        '''
        return 'bigint UNSIGNED'

    def formfield(self, **kwargs):
        defaults = {'min_value': 0,
                    'max_value': BigIntegerField.MAX_BIGINT * 2 - 1}
        defaults.update(kwargs)
        return super(PositiveBigIntegerField, self).formfield(**defaults)


class AshBinary1(models.PositiveSmallIntegerField, AshFieldMixin):
    ''' equivalent to b1 '''
    empty_strings_allowed = False
    description = _('A-Shell B1')

    def __init__(self, *args, **kwargs):
        super(AshBinary1, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(ash_type='b', bytes=1)
        self.index_map_string_varlen = 3

    def get_internal_type(self):
        return 'AshBinary1'


class AshBinary2(models.PositiveSmallIntegerField, AshFieldMixin):
    ''' equivalent to b2 '''
    empty_strings_allowed = False
    description = _('A-Shell b2')

    def __init__(self, *args, **kwargs):
        super(AshBinary2, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(ash_type='b', bytes=2)
        self.index_map_string_varlen = 5

    def get_internal_type(self):
        return 'AshBinary2'


class AshBinary3(models.PositiveIntegerField, AshFieldMixin):
    ''' equivalent to b3 '''
    empty_strings_allowed = False
    description = _('A-Shell b3')

    def __init__(self, *args, **kwargs):
        super(AshBinary3, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(ash_type='b', bytes=3)
        self.index_map_string_varlen = 8

    def get_internal_type(self):
        return 'AshBinary3'


class AshBinary4(models.PositiveIntegerField, AshFieldMixin):
    ''' equivalent to B4 '''
    empty_strings_allowed = False
    description = _('A-Shell B4')

    def __init__(self, *args, **kwargs):
        super(AshBinary4, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(ash_type='b', bytes=4)

    def get_internal_type(self):
        return 'AshBinary4'


class AshBinary6(PositiveBigIntegerField, AshFieldMixin):
    ''' equivalent to B6

    actually stored as 8 byte unsigned integer
    '''
    empty_strings_allowed = False
    description = _('A-Shell b6')

    def __init__(self, *args, **kwargs):
        super(AshBinary6, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(ash_type='b', bytes=6)

    def get_internal_type(self):
        return 'AshBinary6'


class AshFloatBase(models.FloatField, AshFieldMixin):
    ''' base class for A-Shell floats

    - django doesn't have the equivalent of single precision float
    - actually stored as IEEE Double in the database
    '''
    description = _('A-Shell Float')

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        kwargs['null'] = True
        super(AshFloatBase, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(AshFloatBase, self).deconstruct()
        del kwargs['blank']
        del kwargs['null']

    def get_internal_type(self):
        return 'AshFloatBase'


class AshFloat4(AshFloatBase):
    ''' equivalent to F4 '''
    empty_strings_allowed = False
    description = _('A-Shell f4')

    def __init__(self, *args, **kwargs):
        super(AshFloat4, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(ash_type='f', bytes=4)

    def get_internal_type(self):
        return 'AshFloat4'


class AshFloat6(AshFloatBase):
    ''' equivalent to F6 '''
    empty_strings_allowed = False
    description = _('A-Shell f6')

    def __init__(self, *args, **kwargs):
        super(AshFloat6, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(ash_type='f', bytes=6)

    def get_internal_type(self):
        return 'AshFloat6'


class AshFloat8(AshFloatBase):
    ''' equivalent to F8 '''
    empty_strings_allowed = False
    description = _('A-Shell f8')

    def __init__(self, *args, **kwargs):
        super(AshFloat8, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(ash_type='f', bytes=8)

    def get_internal_type(self):
        return 'AshFloat8'


class AshDateTimeCheckMixin(object):
    ''' shared class for enforcing mutually exclusive options '''

    def check(self, **kwargs):
        errors = super(AshDateTimeCheckMixin, self).check(**kwargs)
        errors.extend(self._check_mutually_exclusive_options())
        errors.extend(self._check_fix_default_value())
        return errors

    def _check_mutually_exclusive_options(self):
        # auto_now, auto_now_add, and default are mutually exclusive
        # options. The use of more than one of these options together
        # will trigger an Error
        mutually_exclusive_options = [
            self.auto_now_add, self.auto_now, self.has_default()]
        enabled_options = [option not in (
            None, False) for option in mutually_exclusive_options].count(True)
        if enabled_options > 1:
            return [
                checks.Error(
                    "The options auto_now, auto_now_add, and default "
                    "are mutually exclusive. Only one of these options "
                    "may be present.",
                    obj=self,
                    id='fields.E160',
                )
            ]
        else:
            return []

    def _check_fix_default_value(self):
        return []


class AshJulianDate(AshBinary3, AshDateTimeCheckMixin):
    ''' equivalent to b3 with options to auto set date '''
    # empty_strings_allowed = False
    description = _('A-Shell Julian Date')

    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        '''
        params:
            auto_now - automatically set the field to todays_julian every time saved
            auto_now_add - automatically set the field to todays_julian when first created
        '''
        self.auto_now, self.auto_now_add = auto_now, auto_now_add
        if auto_now or auto_now_add:
            kwargs['editable'] = False
            kwargs['blank'] = True
        super(AshJulianDate, self).__init__(**kwargs)
        # set after calling parent
        self.ash_var_type = AshType(
            def_type='DT_JULIAN',
            ash_type='b',
            bytes=3,
        )

    def has_default(self):
        ''' auto_now, auto_now_add aren't considered defaults in Django
        '''
        # TODO: enforce mutually exclusive options
        # errors = self._check_mutually_exclusive_options()
        # if errors:
        #     raise AshMutuallyExclusiveOptionException(errors)
        has_default = super(AshJulianDate, self).has_default()
        if self.auto_now_add or self.auto_now or has_default:
            return True
        return False

    def get_default(self):
        if self.auto_now_add:
            return 'auto_now_add'
        elif self.auto_now:
            return 'auto_now'
        else:
            return super(AshJulianDate, self).has_default()

    def deconstruct(self):
        name, path, args, kwargs = super(AshJulianDate, self).deconstruct()
        if self.auto_now:
            kwargs['auto_now'] = True
        if self.auto_now_add:
            kwargs['auto_now_add'] = True
        if self.auto_now or self.auto_now_add:
            del kwargs['editable']
            del kwargs['blank']
        return name, path, args, kwargs

    def get_internal_type(self):
        return 'AshJulianDate'


class AshTime(AshBinary3, AshDateTimeCheckMixin):
    ''' equivalent to b3 with options to auto set date '''
    # empty_strings_allowed = False
    description = _('A-Shell Julian Date')

    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        '''
        params:
            auto_now - automatically set the field to todays_julian every time saved
            auto_now_add - automatically set the field to todays_julian when first created
        '''
        self.auto_now, self.auto_now_add = auto_now, auto_now_add
        if auto_now or auto_now_add:
            kwargs['editable'] = False
            kwargs['blank'] = True
        super(AshTime, self).__init__(**kwargs)
        # set after calling parent
        self.ash_var_type = AshType(
            def_type='DT_TIME',
            ash_type='b',
            bytes=3,
        )

    def has_default(self):
        ''' auto_now, auto_now_add aren't considered defaults in Django
        '''
        # TODO: enforce mutually exclusive options
        # errors = self._check_mutually_exclusive_options()
        # if errors:
        #     raise AshMutuallyExclusiveOptionException(errors)
        has_default = super(AshTime, self).has_default()
        if self.auto_now_add or self.auto_now or has_default:
            return True
        return False

    def get_default(self):
        if self.auto_now_add:
            return 'auto_now_add'
        elif self.auto_now:
            return 'auto_now'
        else:
            return super(AshTime, self).has_default()

    def deconstruct(self):
        name, path, args, kwargs = super(AshTime, self).deconstruct()
        if self.auto_now:
            kwargs['auto_now'] = True
        if self.auto_now_add:
            kwargs['auto_now_add'] = True
        if self.auto_now or self.auto_now_add:
            del kwargs['editable']
            del kwargs['blank']
        return name, path, args, kwargs

    def get_internal_type(self):
        return 'AshTime'


class AshString(models.CharField, AshFieldMixin):
    ''' equivalent to string '''
    # empty_strings_allowed = False
    description = _('A-Shell String')

    def __init__(self, *args, **kwargs):
        # don't honor a default value for filler field
        super(AshString, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(
            ash_type='s',
            bytes=kwargs['max_length'])

    def get_internal_type(self):
        return 'AshString'


class AshFiller(models.BinaryField, AshFieldMixin):
    ''' equivalent to unformatted filler '''
    empty_strings_allowed = False
    description = _('A-Shell Filler fields')

    def __init__(self, *args, **kwargs):
        # don't honor a default value for filler field
        kwargs['default'] = None
        super(AshFiller, self).__init__(*args, **kwargs)

        self.ash_var_type = AshType(
            ash_type='x',
            bytes=kwargs['max_length'])

    def deconstruct(self):
        name, path, args, kwargs = super(AshFiller, self).deconstruct()
        del kwargs['default']

    # TODO: if we every migrate these fields to SQL
    # filler doesn't need to be in the database
    def get_internal_type(self):
        return 'AshFiller'


class AshRecordStatus(AshString):
    ''' equivalent to string '''
    # empty_strings_allowed = False
    description = _('A-Shell Record Status')

    def __init__(self, auto_now_add=True, *args, **kwargs):
        self.auto_now_add = True
        kwargs['default'] = 'RECSTAT_ACTIVE'
        kwargs['max_length'] = 1
        super(AshRecordStatus, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(AshRecordStatus, self).deconstruct()
        del kwargs['default']
        del kwargs['max_length']

    def get_internal_type(self):
        return 'AshRecordStatus'


class AshArrayBase(models.BinaryField, AshFieldMixin):
    ''' base class to implement arrays '''
    empty_strings_allowed = False
    description = _('A-Shell Array fields')

    def __init__(self, dimensions, element_length, ash_type, *args, **kwargs):
        super(AshArrayBase, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(
            ash_type=ash_type,
            bytes=element_length,
            array=True,
            dimension_str=dimensions,
        )
        # set max_length to total bytes of array so that database field can store the blob
        kwargs['max_length'] = self.ash_var_type.total_bytes

    # TODO: if we every migrate these fields to SQL
    # the array will have to be stored in a BinaryField
    def get_internal_type(self):
        return 'AshArrayBase'


class AshArrayString(AshArrayBase):
    ''' array string '''
    description = _('A-Shell Array field string')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 's'
        super(AshArrayString, self).__init__(*args, **kwargs)


class AshArrayBinary1(AshArrayBase):
    ''' array Binary 1 '''
    description = _('A-Shell Array field Binary 1')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 'b'
        kwargs['element_length'] = 1
        super(AshArrayBinary1, self).__init__(*args, **kwargs)


class AshArrayBinary2(AshArrayBase):
    ''' array Binary 2 '''
    description = _('A-Shell Array field Binary 2')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 'b'
        kwargs['element_length'] = 2
        super(AshArrayBinary2, self).__init__(*args, **kwargs)


class AshArrayBinary3(AshArrayBase):
    ''' array Binary 3 '''
    description = _('A-Shell Array field Binary 3')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 'b'
        kwargs['element_length'] = 3
        super(AshArrayBinary3, self).__init__(*args, **kwargs)


class AshArrayBinary4(AshArrayBase):
    ''' array Binary 4 '''
    description = _('A-Shell Array field Binary 4')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 'b'
        kwargs['element_length'] = 4
        super(AshArrayBinary4, self).__init__(*args, **kwargs)


class AshArrayBinary5(AshArrayBase):
    ''' array Binary 5 '''
    description = _('A-Shell Array field Binary 5')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 'b'
        kwargs['element_length'] = 5
        super(AshArrayBinary5, self).__init__(*args, **kwargs)


class AshArrayBinary6(AshArrayBase):
    ''' array Binary 6 '''
    description = _('A-Shell Array field Binary 6')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 'b'
        kwargs['element_length'] = 6
        super(AshArrayBinary6, self).__init__(*args, **kwargs)


class AshArrayFloat4(AshArrayBase):
    ''' array Float 4 '''
    description = _('A-Shell Array field Float 4')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 'f'
        kwargs['element_length'] = 4
        super(AshArrayFloat4, self).__init__(*args, **kwargs)


class AshArrayFloat6(AshArrayBase):
    ''' array Float 6 '''
    description = _('A-Shell Array field Float 6')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 'f'
        kwargs['element_length'] = 6
        super(AshArrayFloat6, self).__init__(*args, **kwargs)


class AshArrayFloat8(AshArrayBase):
    ''' array Float 8 '''
    description = _('A-Shell Array field Float 8')

    def __init__(self, *args, **kwargs):
        # override value if passed
        kwargs['ash_type'] = 'f'
        kwargs['element_length'] = 8
        super(AshArrayFloat8, self).__init__(*args, **kwargs)


'''
- The idea here is to create a single db column compositekey
  comprising all the column values.
- the column will be added to the DB table
- you set the values in the member columns and it'll
  combine them automatically
- A-Shell ORM code generation will use this to determine the primary
  keys to use (key_format, DEFSTRUCTS, etc.)
'''

# class AshCompositeKey(object):
#     ''' possible object used in correspondence to AshCompositeKeyField.
#       used only when using Django's ORM, not A-Shell code templating
#     '''
#     def __init__(self, members):
#         '''
#         members - list of columns, in order, comprising the primary key
#         '''
#         self.members = members

ASH_FORMAT_LZEROS = 0
ASH_FORMAT_SPACES = 1

DEFAULT_AUTO_LEAVE = 0
DEFAULT_AUTO_OVERRIDE = 1
DEFAULT_AUTO_NOSET = 2


class AshCompositeKeyField(models.CharField, AshFieldMixin):
    ''' Django field to handle composite keys

    inheriting from CharField because ISAM indexes have to be string
    '''
    empty_strings_allowed = False
    description = _('composite key handler')

    def __init__(self, members, *args, **kwargs):
        '''
        params:
            members    - list of columns, in order, comprising the primary key
            callback   - ** not implemented ** model callback method to allow
                    access to the other model fields
        '''
        # TODO: determine max_length based on max_length of members
        # kwargs['max_length'] = 104
        self.members = members
        super(AshCompositeKeyField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(
            AshCompositeKeyField, self).deconstruct()
        # del kwargs["max_length"]
        return name, path, args, kwargs

    def get_internal_type(self):
        ''' Returns the type of the value expected by the Database. '''
        return 'AshCompositeKeyField'


class AshCompositeKeyMemberField(models.CharField, AshFieldMixin):
    ''' Django field to handle candidate keys

    inheriting from CharField because ISAM indexes have to be string
    '''

    def __init__(self, key_format=ASH_FORMAT_LZEROS, auto_key=False, unique_key=False, *args, **kwargs):
        '''
        params:
            key_format - determines how the value is formatted for ISAM key
            auto_key   - determines if the field member is treated as having an auto generated id
                         (unique to all records in the file)
            unique_key - determines if the field member is treated as having an auto generated id
                         (unique within a subset of records with the same leading field values)
        '''
        self.key_format = key_format
        if auto_key and unique_key:
            raise AshCompositeKeyFieldAutoUniqueException(
                'Composite key field can not be both auto and unique')
        self.auto_key = auto_key
        self.unique_key = unique_key
        super(AshCompositeKeyMemberField, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(
            ash_type='s',
            bytes=kwargs['max_length'])

    def get_internal_type(self):
        ''' Returns the type of the value expected by the Database. '''
        return 'AshCompositeKeyMemberField'


class AshCandidateKeyField(models.CharField, AshFieldMixin):
    ''' Django field to handle candidate keys

    inheriting from CharField because ISAM indexes have to be string
    '''

    def __init__(self, key_format=ASH_FORMAT_LZEROS, *args, **kwargs):
        '''
        params:
            key_format - determines how the value is formatted for ISAM key
        '''
        # kwargs['primary_key'] = True
        self.key_format = key_format
        self.auto_key = True
        super(AshCandidateKeyField, self).__init__(*args, **kwargs)
        self.ash_var_type = AshType(
            ash_type='s',
            bytes=kwargs['max_length'])

    def get_internal_type(self):
        ''' Returns the type of the value expected by the Database. '''
        return 'AshCandidateKeyField'
