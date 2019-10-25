from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('ckk', '0002_auto_20190327_0703'),
    ]
    atomic = True

    operations = [
        migrations.RunSQL(
            f"""insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'KD', 'КД', null , null, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'SPW', 'Спецификация', null, 1, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'CDW', 'Чертеж', null, 1, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' ,'false' ,'SPC_CLM', 'Типы колонок', null, 2, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'SPC_CLM_FORMAT','Формат',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false', 'false' ,'SPC_CLM_ZONE','Зона',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'SPC_CLM_POS','Позиция',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false', 'false' ,'SPC_CLM_MARK','Обозначение',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'SPC_CLM_NAME','Наименование',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false', 'false' ,'SPC_CLM_COUNT','Количество',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'SPC_CLM_NOTE','Примечание',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' , 'SPC_CLM_MASSA','Масса',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'SPC_CLM_MATERIAL','Материал',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'SPC_CLM_USER','Пользовательская',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'SPC_CLM_KOD','Код',null ,4, 1)""",
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified,deleted, editing , deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false', 'false' ,'SPC_CLM_FACTORY','Предприятие - изготовитель',null ,4, 1)""",
        ),
        # ----------------------------------------------------------Атрибуты основной надписи---------------------------------------------
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP', 'Атрибуты основной надписи',null,1, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_1', 'Наименование изделия' , '(в соответствии с требованиями ГОСТ 2.109—73), а также
наименование документа, если этому документу присвоен код. Для изделий народнохозяйственного
назначения допускается не указывать наименование документа, если его код определен ГОСТ
2.102-68, ГОСТ 2.601-95, ГОСТ 2.602-95, ГОСТ 2.701-84; ' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_2', 'Обозначение документа' , '(графу заполняют только на чертежах деталей);' , 17, 1 )"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_3', 'Обозначение материала детали' , '' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_4', 'Литера, присвоенная данному документу' , '(графу заполняют последовательно,
начиная с крайней левой клетки). Допускается в рабочей конструкторской документации литеру проставлять только в спецификациях
и технических условиях.
Для изделий, разрабатываемых по заказу Министерства обороны, перечень конструкторских
документов, на которых должна обязательно проставляться литера, согласуется с заказчиком (представителем
заказчика);' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_5', 'Масса изделия ' , 'по ГОСТ 2.109—73;' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_6', 'Масштаб' , '(проставляется в соответствии с ГОСТ 2.302—68 и ГОСТ 2.109—73); ' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_7', 'Порядковый номер листа' , '(на документах, состоящих из одного листа, графу не
заполняют);' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_8', 'Общее количество листов документа' , '(графу заполняют только на первом листе); ' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_9', 'Наименование или различительный индекс' , 'предприятия, выпускающего документ
(графу не заполняют, если различительный индекс содержится в обозначении документа);' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_10', 'Характер работы' , 'выполняемой лицом, подписывающим документ, в соответствии
с формами 1 и 2. Свободную строку заполняют по усмотрению разработчика, например:
«Начальник отдела», «Начальник лаборатории», «Рассчитал»;' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_110', 'Разраб.' , 'фамилия лица, подписавшего документ;' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_111', 'Пров.' , 'фамилия лица, подписавшего документ;' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_112', 'Т.контр.' , 'фамилия лица, подписавшего документ;' , 17 , 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_113', '10' , 'фамилия лица, подписавшего документ;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_114', 'Н.контр.' , 'фамилия лица, подписавшего документ;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_115', 'Утв.' , 'фамилия лица, подписавшего документ;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_120', 'Разраб.' , 'подписи лиц, фамилии которых указаны в графе 11 (Подписи лиц, разработавших данный документ и ответственных за нормоконтроль, являются
обязательными.)' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_121', 'Пров.' , 'подписи лиц, фамилии которых указаны в графе 11' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_122', 'Т.контр.' , 'подписи лиц, фамилии которых указаны в графе 11' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_123', '10' , 'подписи лиц, фамилии которых указаны в графе 11' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_124', 'Н.контр.' , 'подписи лиц, фамилии которых указаны в графе 11 (Подписи лиц, разработавших данный документ и ответственных за нормоконтроль, являются
обязательными.)' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_125', 'Утв.' , 'подписи лиц, фамилии которых указаны в графе 11 (При отсутствии титульного листа допускается подпись лица, утвердившего документ, размещать
на свободном поле первого или заглавного листа документа в порядке, установленном для
титульных листов по ГОСТ 2.105—95.) Если необходимо на документе наличие визы должостных лиц, то их размещают на поле для
подшивки первого или заглавного листа документа; ' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_130', 'Дата подписания документа;' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_131', 'Дата подписания документа;' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_132', 'Дата подписания документа;' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_133', 'Дата подписания документа;' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_134', 'Дата подписания документа;' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_135', 'Дата подписания документа;' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_140', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_141', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_142', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_150', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_151', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_160', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_161', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_170', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_171', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_180', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_181', 'Изменения' , 'заполняют в соответствии с требованиями
ГОСТ 2.503—90;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_19', 'Инвентарный номер подлинника' , 'по ГОСТ 2.501—88;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_200', 'Подпись' , 'лица, принявшего подлинник в отдел (бюро) технической документации,
и дату приемки;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_201', 'Дата' , 'подписания лицом, принявшего подлинник в отдел (бюро) технической документации,
и дату приемки;
' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_21', 'Инвентарный номер подлинника' , 'взамен которого выпущен данный подлинник
по ГОСТ 2.503-90;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_22', 'Инвентарный номер дубликата' , 'по ГОСТ 2.502—68;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_230', 'Подпись' , 'лица, принявшего дубликат в отдел (бюро) технической документации,
и дату приемки;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_231', 'Дата' , 'подписания лицом, принявшего дубликат в отдел (бюро) технической документации,
и дату приемки;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_24', 'Обозначение документа' , 'взамен или на основании которого выпущен данный
документ. Допускается также использовать графу для указания обозначения документа аналогичного
изделия, для которого ранее изготовлена технологическая оснастка, необходимая для данного
изделия;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_25', 'Обозначение соответствующего документа' , 'в котором впервые записан данный
документ' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_26', 'Обозначение документа' , 'повернутое на 180° для формата А4 и для форматов
больше А4 при расположении основной надписи вдоль длинной стороны листа и на 90° для форматов
больше А4 при расположении основной надписи вдоль короткой стороны листа;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_27', 'Знак, установленный заказчиком' , 'в соответствии с требованиями нормативнотехнической
документации и проставляемый представителем заказчика;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_28', 'Номер решения и год утверждения' , 'документации соответствующей литеры; ' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_29', 'Номер решения и год утверждения' , 'документации' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_30', 'Индекс заказчика' , 'в соответствии с нормативно-технической документацией; ' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_31', 'Подпись' , 'лица, копировавшего чертеж;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_32', 'Обозначение' , 'формата листа по ГОСТ 2.301—68;' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_33', 'Обозначение зоны' , 'в которой находится изменяемая часть изделия; ' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_34', 'Номера авторских свидетельств' , 'на изобретения, использованные в данном изделии.' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_43', 'Полное имя файла содержащего данный документ' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_44', 'Краткое имя файла содержащего данный документ' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_40', '...' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_41', '...' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_45', '...' , '' , 17, 1)"""
        ),
        migrations.RunSQL(
            """insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                    values('NOW()', 'false', 'false' , 'false' ,'STMP_53', '...' , '' , 17, 1)"""
        ),
        # ----------------------------------------------------------End Атрибуты основной надписи-----------------------------------------
        migrations.RunSQL(
            f"""insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                        values('NOW()', 'false', 'false' , 'false' ,'KD_BAD', 'Битая КД', null , null, 1)"""
        ),
        migrations.RunSQL(
            f"""insert into ckk_attr_type(lastmodified , deleted, editing, deliting, code, name, description ,parent_id, props)
                                            values('NOW()', 'false', 'false' , 'false' ,'KD_PDF', 'Бумажная КД', null , null, 1)"""
        ),
    ]
