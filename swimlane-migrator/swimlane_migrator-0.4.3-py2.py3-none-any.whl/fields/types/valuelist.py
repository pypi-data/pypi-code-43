from base.fields import fields

class valuelist(fields):

    def __init__(self, field_obj, source_obj, config ):
        super(valuelist, self).__init__(field_obj, config)
        self.source_object = source_obj

    def migrateValues(self):
        self.logger.debug(self.field_obj)
        target_value_list = self.field_obj['values']
        source_value_list = self.source_object['values']

        new_target_value_list = source_value_list

        ## Add New
        for target_value in new_target_value_list:
            target_value_list_key = self.find_in_list(target_value_list, 'name', target_value['name'])
            ## Add If not found
            if target_value_list_key is not None:
                target_value['id'] = target_value_list[target_value_list_key]['id']

        self.field_obj['values'] = new_target_value_list


        return self.field_obj


    def find_in_list(self, lst, key, value):
        for i, dic in enumerate(lst):
            self.logger.debug('Key: {} Value: {} Check: {}'.format(key, dic[key], value))
            if key in dic and dic[key] == value:
                self.logger.debug('####FOUND####')
                return i
        return None