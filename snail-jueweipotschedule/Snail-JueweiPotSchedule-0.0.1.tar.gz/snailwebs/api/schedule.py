import os
import time
import openpyxl
import json
from flask_restful import Resource
from snailwebs.common.schedule.pot import Schedule


class V1Schedule(Resource):

    def __init__(self):
        self.pBatchData = [[], []]
        self.boilerSState = ['E3', 'F3', 'G3', 'H3', 'I3', 'J3', 'K3', 'L3', 'M3', 'N3']
        self.boilerEStateCount = ['E9', 'F9', 'G9', 'H9', 'I9', 'J9', 'K9', 'L9', 'M9', 'N9']

    @staticmethod
    def __get_datafile_path(date):

        if not date or 'none' == date:
            return os.path.dirname(__file__) + '/../../data/schedule/DATA_' + time.strftime('%Y%m%d') + '.xlsx'

        return os.path.dirname(__file__) + '/../../data/schedule/DATA_' + date + '.xlsx'

    @staticmethod
    def __get_jsonfile_path(date):

        if not date or 'none' == date:
            return os.path.dirname(__file__) + '/../../data/schedule/DATA_' + time.strftime('%Y%m%d') + '.json'

        return os.path.dirname(__file__) + '/../../data/schedule/DATA_' + date + '.json'

    def __parse(self, date):

        # 读取数据
        wb = openpyxl.load_workbook(self.__get_datafile_path(date))
        sheet = wb['数据']

        rowIndex = 4

        while rowIndex < 1000:

            try:
                pId = str(sheet['B' + str(rowIndex)].value)
                pCount = int(sheet['D' + str(rowIndex)].value)
                pId2 = str(sheet['E' + str(rowIndex)].value)
                pCount2 = int(sheet['G' + str(rowIndex)].value)

                self.pBatchData[0].append({"id": pId, "count": pCount})
                self.pBatchData[1].append({"id": pId2, "count": pCount2})
            except:
                pass
            finally:
                rowIndex += 1

        print('Data: %s' % self.pBatchData)


        sheet = wb['配置']
        for i in range(len(self.boilerSState)):
            try:
                self.boilerSState[i] = int(sheet[self.boilerSState[i]].value)
            except:
                self.boilerSState[i] = 0

        for i in range(len(self.boilerEStateCount)):
            try:
                self.boilerEStateCount[i] = int(sheet[self.boilerEStateCount[i]].value)
            except:
                self.boilerEStateCount[i] = 0

        # 合并第0&9圈数量
        self.boilerEStateCount[0] += self.boilerEStateCount[9]
        self.boilerEStateCount.pop()

        print(str(self.boilerSState))

    def __run(self):
        # 排程
        schl = Schedule([5, 6])

        schl.set_boiler_s_states(self.boilerSState)
        schl.set_boiler_e_state_count(self.boilerEStateCount)
        schl.schedule(self.pBatchData)
        schl.print_schedule()
        schl.verify()
        schl.desperse()

        return {
            'SCHEMES_DATA': {
                'boilerSStates': schl.get_boiler_s_states(),
                'boilerEStateCount': schl.get_boiler_e_state_count(),
                'productData': schl.get_product_data()
            },
            'SCHEDULE_DATA': schl.get_schedule()
        }

    def get(self, date):

        result = None
        fpath = self.__get_jsonfile_path(date)

        if os.path.exists(fpath):

            # 读取排程数据
            f = None
            try:
                f = open(fpath, mode='r', encoding='utf-8')
                result = f.read()
                result = json.loads(result)
            finally:
                if f:
                    f.close()
        else:

            if os.path.exists(self.__get_datafile_path(date)):
                self.__parse(date)
                result = self.__run()

                # 保存排程数据
                f = None
                try:
                    f = open(fpath, mode='w', encoding='utf-8')
                    f.write(json.dumps(result))
                    print('保存成功。')
                finally:
                    if f:
                        f.close()
            else:
                pass

        return {"code": "200", "data": result, "message": "成功"}

    def delete(self, date):
        try:
            os.remove(self.__get_jsonfile_path(date))
        except:
            pass
        return {"code": "200", "data": None, "message": "成功"}

    def api_path(self):
        return '/api/schedule/v1/<string:date>'



