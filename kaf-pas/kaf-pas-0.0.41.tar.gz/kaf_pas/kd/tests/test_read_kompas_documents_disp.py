import os
import shutil
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename

import timestring as timestring
from django.test import TestCase

from isc_common.auth.models.user import User
from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.common.constants import constants1, ColumnType
from kaf_pas.common.kompas_api5 import ksDocumentParam, ksDocument2D, ksSpcDocument, ksSpecification, ksSheetPar, ksStamp
from kaf_pas.common.kompas_constants import constants
from kaf_pas.kd.interaction.interaction_kompas_5 import InteractionKompas_5
from kaf_pas.kd.interaction.interaction_kompas_7 import InteractionKompas_7


class Test_Kompas(TestCase):

    def setUp(self):
        self.path = "path"
        self.user = User.objects.get(username='admin')

    # @skip
    def test_kompas5_открытие_Компаса_и_создание_нового_чертежа(self):
        interaction_kompas_3_d = InteractionKompas_5()
        kompas = interaction_kompas_3_d.kompasRun()

        kompas_7 = kompas.ksGetApplication7()
        kompas_7.HideMessage = constants.ksHideMessageNo

        print(kompas_7.ApplicationName(FullName=True))
        self.assertNotEquals(kompas, None)

        document_param = ksDocumentParam(kompas.GetParamStruct(constants.ko_DocumentParam))
        document_param.Init()
        document_param.type = constants.ksDocumentDrawing

        document2_d = ksDocument2D(kompas.Document2D())
        document2_d.ksCreateDocument(document_param)

        kompas.Visible = True

        time.sleep(5)
        kompas.Quit()
        time.sleep(5)

    # @skip
    def test_kompas5_открытие_Компаса_и_создание_новой_спецификации(self):
        interaction_kompas_3_d = InteractionKompas_5()
        kompas = interaction_kompas_3_d.kompasRun()
        kompas_7 = kompas.ksGetApplication7()
        kompas_7.HideMessage = constants.ksHideMessageNo

        print(kompas_7.ApplicationName(FullName=True))
        self.assertNotEquals(kompas, None)

        document_param = ksDocumentParam(kompas.GetParamStruct(constants.ko_DocumentParam))
        document_param.Init()
        document_param.type = 4  # lt_DocSpc
        document_param.regime = 0  # визуальный режим

        # Получаем  интерфейс параметров листа
        sheet_par = ksSheetPar(document_param.GetLayoutParam())
        sheet_par.Init()

        # Указываем библиотеку стилей
        ################################ По умолчанию принимается graphic.lyt #############################################################
        # str = kompas.ksSystemPath(0) + '\\graphic.lyt'
        # sheet_par.layoutName = str

        # Получаем интерфейс документа - спецификации
        spc_document = ksSpcDocument(kompas.SpcDocument())

        # Создаем спецификацию
        spc_document.ksCreateDocument(document_param)

        # Открываем существующую спецификацию
        kompas.Visible = True

        time.sleep(5)
        kompas.Quit()
        time.sleep(5)

    # @skip
    def test_kompas5_открытие_Компаса_и_наполнение_спецификации(self):
        interaction_kompas_3_d = InteractionKompas_5()
        kompas = interaction_kompas_3_d.kompasRun()
        kompas_7 = kompas.ksGetApplication7()
        kompas_7.HideMessage = constants.ksHideMessageNo

        print(kompas_7.ApplicationName(FullName=True))
        self.assertNotEquals(kompas, None)

        document_param = ksDocumentParam(kompas.GetParamStruct(constants.ko_DocumentParam))
        document_param.Init()
        document_param.type = 4  # lt_DocSpc
        document_param.regime = 0  # визуальный режим

        # Получаем  интерфейс параметров листа
        sheet_par = ksSheetPar(document_param.GetLayoutParam())
        sheet_par.Init()

        # Указываем библиотеку стилей
        # По умолчанию принимается graphic.lyt
        nameLib = kompas.ksSystemPath(0) + '\\graphic.lyt'
        sheet_par.layoutName = nameLib

        # Получаем интерфейс документа - спецификации
        spc_document = ksSpcDocument(kompas.SpcDocument())

        # Создаем спецификацию
        spc_document.ksCreateDocument(document_param)

        # Получаем интерфейс ksSpecification
        specification = ksSpecification(spc_document.GetSpecification())

        typeObj = 1
        # Cоздаем раздел "Документация"
        specification.ksSpcObjectCreate(nameLib=nameLib, styleNumb=1, secNumb=constants1.documentation, subSecNumb=0, numb=0, typeObj=typeObj)
        # Заполняем колонку "Наименование"
        specification.ksSetSpcObjectColumnText(ColumnType.SPC_CLM_NAME, 1, 0, 'Спецификация')
        # Заполняем колонку "Количество"
        specification.ksSpcCount(0, '1')
        # Закрываем объект в разделе "Документация"
        specification.ksSpcObjectEnd()

        # Создаем раздел "Детали"
        specification.ksSpcObjectCreate(nameLib=nameLib, styleNumb=1, secNumb=constants1.minutiae, subSecNumb=0, numb=0, typeObj=typeObj)
        # Заполняем колонку "Наименование"
        specification.ksSetSpcObjectColumnText(ColumnType.SPC_CLM_NAME, 1, 0, 'Крышка')
        # Заполняем колонку "Формат"
        specification.ksSetSpcObjectColumnText(ColumnType.SPC_CLM_FORMAT, 1, 0, 'А3')
        # Заполняем колонку "Количество"
        specification.ksSpcCount(0, '2')
        # Заполняем колонку "Позиция"
        specification.ksSpcPosition(1)
        # Заполняем колонку "Масса"
        specification.ksSpcMassa('25')
        # Закрываем объект в разделе "Детали"
        specification.ksSpcObjectEnd()

        # Открываем существующую спецификацию
        kompas.Visible = True

        time.sleep(5)
        kompas.Quit()
        time.sleep(5)

    # @skip
    def test_kompas5_открытие_Компаса_и_чтение_спецификации(self):
        interaction_kompas_3_d = InteractionKompas_5()
        kompas = interaction_kompas_3_d.kompasRun()
        kompas_7 = kompas.ksGetApplication7()
        kompas_7.HideMessage = constants.ksHideMessageNo

        print(kompas_7.ApplicationName(FullName=True))
        self.assertNotEquals(kompas, None)

        root = Tk()
        root.withdraw()  # Скрываем основное окно и сразу окно выбора файлов

        filename = askopenfilename(title="Выберите файл спецификации ", filetypes=[('Файлы спецификаций, "Компас 3D"', '*.spw'), ])

        def prnt(spec_row, sectionName, document):
            print(
                f"format: {spec_row.format} zone: {spec_row.zone} pos: {spec_row.pos} mark: {spec_row.mark} name: {spec_row.name} count: {spec_row.count} note: {spec_row.note} massa: {spec_row.massa} material: {spec_row.material} user: {spec_row.user} code: {spec_row.code} factory: {spec_row.factory}")

        # Получаем интерфейс документа - спецификации
        spc_document = ksSpcDocument(kompas.SpcDocument())
        # Открываем существующую спецификацию
        res_opening = spc_document.ksOpenDocument(filename, 0)

        if not res_opening:
            raise Exception(f'Документ: {filename} не открыт !!!!!!!')

        InteractionKompas_5.readSpecification(spc_document, kompas, prnt)

        kompas.Visible = True

        root.destroy()  # Уничтожаем основное окно
        root.mainloop()

    def print(self, text, index, document):
        code = f"STMP_{index}"
        attr = Attr_type.objects.get_attr(code=code)
        if attr:
            print(f"{attr.name}({index}): {text}")
        else:
            print(f"Unknown ({index}): {text}")

    # @skip
    def test_kompas5_открытие_Компаса_и_чтение_штампа_из_спецификации(self):
        interaction_kompas_3_d = InteractionKompas_5()
        kompas = interaction_kompas_3_d.kompasRun()
        kompas_7 = kompas.ksGetApplication7()
        kompas_7.HideMessage = constants.ksHideMessageNo

        print(kompas_7.ApplicationName(FullName=True))
        self.assertNotEquals(kompas, None)

        root = Tk()
        root.withdraw()  # Скрываем основное окно и сразу окно выбора файлов

        filename = askopenfilename(title="Выберите файл спецификации ", filetypes=[('Файлы спецификаций, "Компас 3D"', '*.spw'), ])
        # Получаем интерфейс документа - спецификации
        spc_document = ksSpcDocument(kompas.SpcDocument())
        # Открываем существующую спецификацию в "слепом" (без вывода на экран) варианте
        res_opening = spc_document.ksOpenDocument(filename, 1)
        if not res_opening:
            raise Exception(f'Документ: {filename} не открыт !!!!!!!')

        # Чтение штампа
        stamp = ksStamp(spc_document.GetStamp())
        InteractionKompas_5.readStampItem(kompas=kompas, stamp=stamp, function=self.print, document=None)
        stamp.ksCloseStamp()

        root.destroy()  # Уничтожаем основное окно
        root.mainloop()
        kompas.Quit()

    # @skip
    def test_kompas5_открытие_Компаса_и_чтение_штампа_из_чертежа(self):
        interaction_kompas_3_d = InteractionKompas_5()
        kompas = interaction_kompas_3_d.kompasRun()
        kompas_7 = kompas.ksGetApplication7()
        kompas_7.HideMessage = constants.ksHideMessageNo

        print(kompas_7.ApplicationName(FullName=True))
        self.assertNotEquals(kompas, None)

        root = Tk()
        root.withdraw()  # Скрываем основное окно и сразу окно выбора файлов

        filename = askopenfilename(title="Выберите файл чертежа ", filetypes=[('Файлы чертежей, "Компас 3D"', '*.cdw'), ])
        # Получаем интерфейс документа - чертежа
        document2_d = ksDocument2D(kompas.Document2D())
        # Открываем существующую спецификацию в "слепом" (без вывода на экран) варианте
        res_opening = document2_d.ksOpenDocument(filename, 1)
        if not res_opening:
            raise Exception(f'Документ: {filename} не открыт !!!!!!!')

        # Чтение штампа
        stamp = ksStamp(document2_d.GetStamp())

        InteractionKompas_5.readStampItem(kompas=kompas, stamp=stamp, function=self.print, document=None)
        stamp.ksCloseStamp()

        root.destroy()  # Уничтожаем основное окно
        root.mainloop()

        kompas.Quit()

    def test_kompas5_открытие_Компаса_и_сохранение_чертежа_в_растровом_формате(self):
        interaction_kompas_3_d = InteractionKompas_5()
        kompas = interaction_kompas_3_d.kompasRun()
        kompas_7 = kompas.ksGetApplication7()
        kompas_7.HideMessage = constants.ksHideMessageNo

        print(kompas_7.ApplicationName(FullName=True))
        self.assertNotEquals(kompas, None)

        root = Tk()
        root.withdraw()  # Скрываем основное окно и сразу окно выбора файлов

        filename = askopenfilename(title="Выберите файл чертежа ", filetypes=[('Файлы чертежей, "Компас 3D"', '*.cdw'), ])

        dir_tmp = f'c:{os.path.altsep}tmp_thumb'

        if os.path.exists(dir_tmp):
            shutil.rmtree(dir_tmp)
        os.mkdir(dir_tmp)

        # Получаем интерфейс чертежа
        document2_d = ksDocument2D(kompas.Document2D())
        # Открываем существующую спецификацию в "слепом" (без вывода на экран) варианте
        res_opening = document2_d.ksOpenDocument(filename, 1)
        if not res_opening:
            raise Exception(f'Документ: {filename} не открыт !!!!!!!')

        interactionKompas = InteractionKompas_5()
        files = interactionKompas.save_2_rastr(document=document2_d, filename=filename, scale=1.0, dir=dir_tmp)
        for file in files:
            print(file)
        root.destroy()  # Уничтожаем основное окно
        root.mainloop()

        kompas.Quit()

    def test_kompas5_открытие_Компаса_и_сохранение_спецификации_в_растровом_режиме(self):
        interaction_kompas_3_d = InteractionKompas_5()
        kompas = interaction_kompas_3_d.kompasRun()
        kompas_7 = kompas.ksGetApplication7()
        kompas_7.HideMessage = constants.ksHideMessageNo

        dir_tmp = f'c:{os.path.altsep}tmp_thumb'

        if os.path.exists(dir_tmp):
            shutil.rmtree(dir_tmp)
        os.mkdir(dir_tmp)

        print(kompas_7.ApplicationName(FullName=True))
        self.assertNotEquals(kompas, None)

        root = Tk()
        root.withdraw()  # Скрываем основное окно и сразу окно выбора файлов

        filename = askopenfilename(title="Выберите файл спецификации ", filetypes=[('Файлы спецификаций, "Компас 3D"', '*.spw'), ])

        # Получаем интерфейс документа - спецификации
        spc_document = ksSpcDocument(kompas.SpcDocument())
        # Открываем существующую спецификацию в "слепом" (без вывода на экран) варианте
        res_opening = spc_document.ksOpenDocument(filename, 1)
        if not res_opening:
            raise Exception(f'Документ: {filename} не открыт !!!!!!!')

        interactionKompas = InteractionKompas_5()
        files = interactionKompas.save_2_rastr(document=spc_document, filename=filename, scale=0.1, dir=dir_tmp)
        for file in files:
            print(file)

        root.destroy()  # Уничтожаем основное окно
        root.mainloop()

        kompas.Quit()

    # @skip
    def test_kompas7Run(self):
        interaction_kompas_3_d = InteractionKompas_7()
        res = interaction_kompas_3_d.kompasRun()
        self.assertNotEquals(res, None)
        res.Visible = True
        # res.Quit()
        # time.sleep(2)

    def test_str_2_date(self):
        print(timestring.Date('01/01/2018'))

# E:/KAF/Кузова/К5350/К5350-11-003/К5350-11-003(1174-1.3) Пенза Рубин 18-109/Надрамник/К5350-11-003(1174-1.3).00.00.100.spw
