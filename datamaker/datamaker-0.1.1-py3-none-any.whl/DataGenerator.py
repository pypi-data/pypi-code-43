from random import randint

from .CodeGenLogic import convert_common_ds_to_ts, timestamp_add_seconds, datestamp_add_days, get_date_diff_days, \
    get_time_diff_seconds, create_email, get_name_columns, set_default_boundary_conditions, set_is_null, \
    get_val_from_fixed_map, set_float_val

from .ValidationLogic import validate_num_rows, validate_column_defs, check_common_ts_format, validate_metadata_types, \
    validate_path

from .common.Common import open_json, get_random_val_from_list

from .common.paths import names_path, streets_path, cities_path, states_path, countries_path, parameters_path


class DataGen(object):
    """ super class for building tabular datasets """
    def __init__(self, table_name, num_rows, column_defs, path):
        self.path = path
        self.table_name = table_name
        self.num_rows = num_rows
        self.column_defs = column_defs
        self.validate_params()


    def validate_params(self):
        """ validate the num_rows and column_defs parameters. Return True if valid """
        validate_num_rows(self.num_rows)
        validate_metadata_types(self.column_defs)
        validate_path(self.path)
        for column_name in self.column_defs:
            validate_column_defs(column_name, self.column_defs)
        return True

    def get_name(self):
        jsondata = open_json(names_path)
        names = jsondata.get("names")
        name = get_random_val_from_list(names)
        return name

    def get_email(self, rowdata):
        name_columns = get_name_columns(self.column_defs)
        name_col1 = name_columns[0]
        name1 = rowdata[name_col1]
        name2 = None
        if len(name_columns) > 1:
            name_col2 = name_columns[1]
            name2 = rowdata[name_col2]
        email = create_email(name1, name2)
        return email

    def get_address(self):
        """ returns num street city state """
        streets_json = open_json(streets_path)
        streets = streets_json["streets"]
        suffixes = streets_json["suffixes"]
        cities = open_json(cities_path)["cities"]
        states = open_json(states_path)

        num = randint(20, 8000)
        street = get_random_val_from_list(streets)
        suffix = get_random_val_from_list(suffixes)
        city = get_random_val_from_list(cities)
        state = get_random_val_from_list(states)["abbreviation"]

        address = "{num} {street} {suffix} {city} {state}".format(
            num=num,
            street=street,
            suffix=suffix,
            city=city,
            state=state
        )
        return address

    def get_timestamp(self, lowerbnd, upperbnd):
        """ returns a random timestamp between lowerbnd and upperbnd """
        if not check_common_ts_format(lowerbnd):
            lowerbnd = convert_common_ds_to_ts(lowerbnd)

        if not check_common_ts_format(upperbnd):
            upperbnd = convert_common_ds_to_ts(upperbnd)

        diff_seconds = get_time_diff_seconds(lowerbnd, upperbnd)
        jump_size = diff_seconds / self.num_rows
        seconds = jump_size * randint(0, self.num_rows)
        ts = timestamp_add_seconds(lowerbnd, seconds)
        return ts

    def get_date(self, lowerbnd, upperbnd):
        """ returns a random date between lowerbnd and upperbnd """
        diff_days = get_date_diff_days(lowerbnd, upperbnd)
        jump_size = diff_days / self.num_rows
        days = jump_size * randint(0, self.num_rows)
        ds = datestamp_add_days(lowerbnd, days)
        return ds

    def get_country(self):
        """ return an ISO 3166-1 alpha-2 codes """
        jsondata = open_json(countries_path)
        country_tuple = get_random_val_from_list(jsondata)
        code = country_tuple["code"]
        return code

    def get_state(self):
        """ return a two letter US state abbreviation """
        jsondata = open_json(states_path)
        state_tuple = get_random_val_from_list(jsondata)
        code = state_tuple["abbreviation"]
        return code

    def get_metadata(self, column_name):
        metadata_defs_json = open_json(parameters_path)
        parameters = metadata_defs_json["parameter"]

        metadata = self.column_defs.get(column_name)

        col_metadata = tuple(map(lambda param: metadata.get(param), parameters))
        return col_metadata

    def generate_data(self, collection):
        """ constructs a dict of randomized data within bounds and specifications
            laid out in column_defs object """
        row_values = {}
        for column_name in self.column_defs:
            col_type, varchar_length, is_primary_key, is_name, is_email, is_date, \
            is_timestamp, is_country, is_state, is_address, bounds, fixed_collection, \
            fixed_map, is_nullable, proportion_null = self.get_metadata(column_name)

            collected_values = collection.get(column_name)

            if bounds:
                lowerbnd = bounds[0]
                upperbnd = bounds[1]
            else:
                lowerbnd, upperbnd = set_default_boundary_conditions(column_name, self.column_defs)

            if is_nullable:
                is_null = set_is_null(proportion_null)
            else:
                is_null = False

            if is_primary_key:
                if not collected_values:
                    val = 1
                else:
                    val = collected_values[-1] + 1

            elif is_null:
                val = 'NULL'

            elif fixed_collection:
                val = get_random_val_from_list(fixed_collection)

            elif fixed_map:
                val = get_val_from_fixed_map(fixed_map, row_values)

            elif col_type == "int":
                val = randint(lowerbnd, upperbnd)

            elif col_type == "float":
                val = set_float_val(lowerbnd, upperbnd)

            elif col_type == "varchar":
                if is_name:
                     val = self.get_name()
                elif is_email:
                    val = self.get_email(row_values)
                elif is_address:
                    val = self.get_address()
                elif is_date:
                    val = self.get_date(lowerbnd, upperbnd)
                elif is_timestamp:
                    val = self.get_timestamp(lowerbnd, upperbnd)
                elif is_country:
                    val = self.get_country()
                elif is_state:
                    val = self.get_state()
            elif col_type == "bool":
                val = randint(0, 1) == 1

            row_values[column_name] = val
            if collected_values:
                collected_values.append(val)
            else:
                collection[column_name] = [val]

        return row_values, collection
