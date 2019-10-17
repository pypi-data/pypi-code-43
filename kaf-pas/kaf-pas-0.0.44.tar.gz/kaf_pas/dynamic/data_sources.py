class Dynamic:

    def get_datasources(self):
        from kaf_pas.ckk.models.material_params import Material_params
        from kaf_pas.ckk.models.material_type import Material_type
        from refs.models.type_param import Type_param

        def uncapitalize(str):
            return str[0:1].lower() + str[1:]

        data_sources = []
        for material_type in Material_type.objects.all():
            step = 0
            fields = []
            for param in Material_params.objects.filter(materials_type=material_type).order_by('order', ):
                if param.param_type.type == Type_param.integer():
                    fields.append(f'unstackedSpinnerField("{param.param_type.code}", "{param.param_type.name}", {uncapitalize(str(param.param_type.required))})')
                elif param.param_type.type == Type_param.float():
                    fields.append(f'floatField("{param.param_type.code}", "{param.param_type.name}", {uncapitalize(str(param.param_type.required))})')
                elif param.param_type.type == Type_param.date():
                    fields.append(f'dateField("{param.param_type.code}", "{param.param_type.name}", {uncapitalize(str(param.param_type.required))})')
                elif param.param_type.type == Type_param.date_time():
                    fields.append(f'dateTimeField("{param.param_type.code}", "{param.param_type.name}", {uncapitalize(str(param.param_type.required))})')
                elif param.param_type.type == Type_param.string():
                    fields.append(f'nameField("{param.param_type.code}", "{param.param_type.name}", {uncapitalize(str(param.param_type.required))}, false, {param.param_type.length if param.param_type.length else 255})')
                elif param.param_type.type == Type_param.select():
                    fields.append(f'selectField("{param.param_type.code}", "{param.param_type.name}", {param.param_type.value_map}, {uncapitalize(str(param.param_type.required))})')
                else:
                    raise Exception(f'{param.param_type.type}: unknown type.')

            step += 1
            identifier = material_type.code
            data_source = '''isc.RestDataSourceSS.create(
                {
                    identifier: "$identifier",
                    fields: $FIELDS,
                    addDataURL: "logic/Material_added_values/Add",
                    fetchDataURL: "logic/Material_added_values/Fetch/",
                    removeDataURL: "logic/Material_added_values/Remove",
                    updateDataURL: "logic/Material_added_values/Update",
                    lookupDataURL: "logic/Material_added_values/Lookup/",
                    infoDataURL: "logic/Material_added_values/Info/",
                    copyDataURL: "logic/Material_added_values/Copy",
                })
            '''
            data_source = data_source.replace('$FIELDS', f"[{','.join(fields)}]")
            data_source = data_source.replace('$identifier', identifier).replace(' ', '').replace('\n', '')
            data_sources.append(data_source)
        sql_str = ','.join(data_sources)
        sql_str = f'[{sql_str}]'
        return sql_str
