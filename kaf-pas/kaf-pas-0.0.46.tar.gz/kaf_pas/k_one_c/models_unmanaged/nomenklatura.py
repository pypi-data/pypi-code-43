from one_c.models.entities import EntityProperties, Field


class Nomenklatura(EntityProperties):
    code = 'Номенклатура'

    def used_field(self):
        return [
            Field(name='Ref', primary_key=True, title='ID', hidden=True, type=Field.uuid()),
            Field(name='Code', title='Код номенклатуры (1C)', lookup=True, canSort=True),
            Field(name='full_name', title='Полное наименование номенклатуры (1C)', lookup=True, canSort=False, canEdit=False, canFilter=False, only_datasource=True),
            Field(name='Description', title='Наименование номенклатуры (1C)', lookup=True, canSort=True),
            Field(name='Parent', hidden=True, type=Field.uuid()),
            Field(name='IsFolder', hidden=True, type=Field.boolean()),
            Field(name='НаименованиеПолное', title='Полное наименование номенклатуры  (1C)', lookup=True, canSort=True),
            Field(name='ВидНоменклатуры', hidden=True, type=Field.uuid()),
            Field(name='ЕдиницаДляОтчетов', hidden=True, type=Field.uuid()),
        ]
