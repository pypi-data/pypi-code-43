""" File to get the updated metadata file with custom statistics"""
from collections import OrderedDict
import re
import json
import raven_preprocess.col_info_constants as col_const
from raven_preprocess.column_info import ColumnInfo
from raven_preprocess.np_json_encoder import NumpyJSONEncoder
from raven_preprocess.version_number_util import VersionNumberUtil

ALL_VARIABLE_ATTRIBUTES = [x[0] for x in ColumnInfo.get_variable_labels()]
VIEWABLE_VALUES = [True, False]
CUSTOM_STATISTICS_NAME = 'name'
CUSTOM_STATISTICS_VARIABLES = 'variables'
CUSTOM_STATISTICS_IMAGE = 'image'
CUSTOM_STATISTICS_DESCRIPTION = 'description'
CUSTOM_STATISTICS_REPLICATION = 'replication'
CUSTOM_STATISTICS_VIEWABLE = 'viewable'
CUSTOM_STATISTICS_VALUE = 'value'
CUSTOM_STATISTICS_DELETE = 'delete'
CUSTOM_STATISTICS_UPDATE = 'updates'
CUSTOM_STATISTICS_ID = 'id'


class CustomStatisticsUtil(object):
    def __init__(self, preprocess_json, custom_statistics_json):
        """class for the custom statistics process"""

        assert isinstance(preprocess_json, dict),\
            "preprocess_json must be a dict/OrderedDict"

        self.preprocess_json = preprocess_json
        self.custom_statistics_json = custom_statistics_json

        # for error handling
        self.has_error = False
        self.error_messages = []
        self.original_json = None

        # call the statistic function

    def add_error_message(self, err_msg):
        """Add error message"""
        # print(err_msg)
        self.has_error = True
        self.error_messages.append(err_msg)

    def get_updated_metadata(self, as_string=False):
        """Return the modified metadata--which is in the 'original_json' """
        assert self.has_error is False, \
            "Make sure that 'has_error' is False before using this method"

        if as_string:
            return json.dumps(self.original_json,
                              indent=4,
                              cls=NumpyJSONEncoder)

        return self.original_json

    def get_error_messages(self):
        """Return the list of error messages"""
        print("Error messages ", self.error_messages)
        return self.error_messages

    def custom_statistics_create_id(self):   # need to think of generating id
        if col_const.CUSTOM_KEY not in self.preprocess_json:
            var_id = 'id_000001'
        else:
            ids = list(self.preprocess_json[col_const.CUSTOM_KEY])
            ids.sort()
            latest_id = ids[-1]
            _unused, idnum = latest_id.split('_')
            next_num = str(int(idnum) + 1)
            var_id = 'id_%s' % next_num.zfill(6)
        return var_id

    def custom_statistics_check_name(self, name):
        statistics_name = name
        if not re.match(r'^[A-Za-z0-9_]+$', statistics_name):   # check if the name is alpha numerics , \
                                            #  i.e does not contain special characters or empty spaces
            self.add_error_message('The name is not valid (Should be alpha-numeric)')
        # if col_const.CUSTOM_KEY in self.preprocess_json:
            # for val in self.preprocess_json[col_const.CUSTOM_KEY]:
            #     print("Value coming ",self.preprocess_json[col_const.CUSTOM_KEY][val]['name'])
            #     if name == self.preprocess_json[col_const.CUSTOM_KEY][val]['name']:
            #         print("******** error **********")
            #         self.add_error_message('The variable name %s already exist in the metadata file' % name)
        return statistics_name

    def custom_statistics_check_variables(self, var_list, variables):
        # print("all var ", var_list)
        for var in variables:
            if var not in var_list:
                self.add_error_message('The variable %s does not exist in the metadata file' % var)

        return variables

    def custom_statistics_check_image(self, image_url):
        if image_url is None:
            self.add_error_message('image url not found!')

        return image_url

    @staticmethod
    def is_major_update():
        """add or change a custom stat"""
        return False

    @staticmethod
    def is_minor_update():
        """add or change a custom stat"""
        return True

    def custom_statistics_check_value(self, value):
        if value is None:
            self.add_error_message(' value not found ')

        return value

    def custom_statistics_check_description(self, desc):
        if desc is None:
            self.add_error_message(' description not found!')
            return

        return desc

    def custom_statistics_check_replication(self, rep):
        if rep is None:
            self.add_error_message(' replication not found! ')
            return

        return rep

    def custom_statistics_check_viewable(self, viewable):
        if viewable not in VIEWABLE_VALUES:
            self.add_error_message('Viewable should be either True or False')
            return
        return viewable

    def custom_statistics_update(self):
        """Main function for appending the data"""
        """
               sample Update json coming :
               {
          "preprocess_id":1677,
          "custom_statistics":[
             {
                "name":"Third order statistic",
                "variables":"lpop,bebop",
                "image":"http://www.google.com",
                "value":23.45,
                "description":"Third smallest value",
                "replication":"sorted(X)[2]",
                "omit":false
             },
             {
                "name":"Fourth order statistic",
                "variables":"pop,bebop",
                "image":"http://www.youtube.com",
                "value":29.45,
                "description":"Fourth smallest value",
                "replication":"sorted(X)[3]",
                "omit":false
             }
          ]
       }
               """
        # preprocess_id = self.custom_statistics_json['preprocess_id']
        var_list = list(self.preprocess_json[CUSTOM_STATISTICS_VARIABLES])

        for dat in self.custom_statistics_json:
            # print("dat ", dat)
            if CUSTOM_STATISTICS_NAME in dat:
                name = self.custom_statistics_check_name(dat[CUSTOM_STATISTICS_NAME])   # required = True
            else:
                name = ''
                self.add_error_message(' name is required')
            # id = self.custom_statistics_create_id(name)
            if CUSTOM_STATISTICS_VARIABLES in dat:

                variables = self.custom_statistics_check_variables(var_list,
                                                                   dat[CUSTOM_STATISTICS_VARIABLES])   # required = True
            else:
                variables = ''
                self.add_error_message(' at least one variable is required')

            if CUSTOM_STATISTICS_IMAGE in dat:
                image = self.custom_statistics_check_image(dat[CUSTOM_STATISTICS_IMAGE])
            else:
                image = []

            if CUSTOM_STATISTICS_VALUE:
                value = self.custom_statistics_check_value(dat[CUSTOM_STATISTICS_VALUE])    # required = True
            else:
                value = ''
                self.add_error_message(' value is required')

            if CUSTOM_STATISTICS_DESCRIPTION in dat:
                description = self.custom_statistics_check_description(dat[CUSTOM_STATISTICS_DESCRIPTION])
            else:
                description = None

            if CUSTOM_STATISTICS_REPLICATION in dat:
                replication = self.custom_statistics_check_replication(dat[CUSTOM_STATISTICS_REPLICATION])
            else:
                replication = None

            if CUSTOM_STATISTICS_VIEWABLE in dat:
                viewable = self.custom_statistics_check_viewable(dat[CUSTOM_STATISTICS_VIEWABLE])
            else:
                viewable = True  # default
            if self.has_error:
                return False
            else:
                data = {
                        CUSTOM_STATISTICS_NAME: name,
                        CUSTOM_STATISTICS_VARIABLES: variables,
                        CUSTOM_STATISTICS_IMAGE: image,
                        CUSTOM_STATISTICS_VALUE: value,
                        CUSTOM_STATISTICS_DESCRIPTION: description,
                        CUSTOM_STATISTICS_REPLICATION: replication,
                        "display": {
                            CUSTOM_STATISTICS_VIEWABLE: viewable
                        }

                    }

                self.add_to_original(data)

        self.original_json = OrderedDict(self.preprocess_json)

        success, updated_or_err = VersionNumberUtil.update_version_number(
                                        self.original_json,
                                        self.is_major_update())


        if not success:
            self.add_error_message(updated_or_err)
            return False

    def add_to_original(self, data):
        id_name = self.custom_statistics_create_id()
        # self.original_json= self.preprocess_json
        if col_const.CUSTOM_KEY not in self.preprocess_json:
            self.preprocess_json[col_const.CUSTOM_KEY] = {id_name: data}
        else:
            self.preprocess_json[col_const.CUSTOM_KEY][id_name] = data

        # print(self.original_json)

    # update functions for custom_stats_update

    def check_ids(self, id_name):
        """check for id"""
        id_list = list(self.preprocess_json[col_const.CUSTOM_KEY])    # return list of ids
        # print("id name and id list ", id_name, id_list)
        if id_name in id_list:
            # print(' id %s is there ' % id_name)
            return True, None
        else:
            return False, ' id %s not found in requested update' % id_name

    def make_update(self, id_name, update_json):
        """ make changes to preprocess json"""
        for val in update_json:
            # print(" this is val ", val)
            # print("this is the updateing object ", self.preprocess_json['custom_statistics'][id])
            try:
                self.preprocess_json[col_const.CUSTOM_KEY][id_name][val] = update_json[val]
            except KeyError:
                self.add_error_message('%s not present in the preprocess file ' % val)
                return False

    def basic_update_structure_check(self, update_json, type_input):
        """ check if all updates has update and ids"""
        search = None
        if type_input == CUSTOM_STATISTICS_DELETE:
            search = CUSTOM_STATISTICS_DELETE
        elif type_input == CUSTOM_STATISTICS_UPDATE:
            search = CUSTOM_STATISTICS_UPDATE
        if CUSTOM_STATISTICS_ID not in update_json:
            # self.add_error_message('id section is not present in request')
            return False, 'id section is not present in request'
        if search not in update_json:
            # self.add_error_message('%s section not present in request' % search)
            return False, '%s section not present in request' % search

        return True, None

    def update_custom_stats(self):
        """ The update is done here"""
        """ Sample update_json
                 [
            {
              "id": "id_1",
              "updates": {
                "name": "Fourth order statistic",
                "value": 40
              }
            },
            {
              "id": "id_2"
              "updates": {
                "name": "This will be a new statistic",
                "value": 40
              }
            }
          ]
        """
        # going through each update
        for update in self.custom_statistics_json:
            check, msg = self.basic_update_structure_check(update, CUSTOM_STATISTICS_UPDATE)
            if check is False:
                self.add_error_message(msg)

            id_check, msg = self.check_ids(update[CUSTOM_STATISTICS_ID])
            if id_check is False:
                self.add_error_message(msg)

            if not self.has_error:
                self.make_update(update[CUSTOM_STATISTICS_ID], update[CUSTOM_STATISTICS_UPDATE])

        self.original_json = OrderedDict(self.preprocess_json)
        success, updated_or_err = VersionNumberUtil.update_version_number(self.original_json, self.is_major_update())
        if not success:
            self.add_error_message(updated_or_err)
            return False
        # print("updates to custom_statistics : ", self.original_json)

    def make_deletion(self, id_num, update):
        """ here we delete"""
        if CUSTOM_STATISTICS_ID in update:
            del self.preprocess_json[col_const.CUSTOM_KEY][id_num]
        else:
            for val in update:
                try:
                    del self.preprocess_json[col_const.CUSTOM_KEY][id_num][val]
                except KeyError:
                    self.add_error_message('%s not present in file' % val)
                    return False

    def delete_custom_stat(self):
        """ delete fields/custom stats"""
        # print("custom json ", self.custom_statistics_json)
        for delete_obj in self.custom_statistics_json:
            # print("this is delete obj ", delete_obj)
            check, msg = self.basic_update_structure_check(delete_obj, CUSTOM_STATISTICS_DELETE)
            if not check:
                self.add_error_message(msg)

            id_check, msg = self.check_ids(delete_obj[CUSTOM_STATISTICS_ID])
            if id_check is False:
                self.add_error_message(msg)

            if not self.has_error:
                self.make_deletion(delete_obj[CUSTOM_STATISTICS_ID], delete_obj[CUSTOM_STATISTICS_DELETE])

        self.original_json = OrderedDict(self.preprocess_json)

        # print("After deletion ", self.original_json)

        success, updated_or_err = VersionNumberUtil.update_version_number(self.original_json,
                                                                          self.is_major_update())
        if not success:
            self.add_error_message(updated_or_err)
            return False
