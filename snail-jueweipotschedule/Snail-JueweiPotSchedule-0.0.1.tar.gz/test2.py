import os
import openpyxl
import json
from snailwebs.common.schedule import Schedule

# 读取数据
wb = openpyxl.load_workbook('./data.xlsx')
sheet = wb['数据']
pBatchData = [[], []]

rowIndex = 4

while rowIndex < 1000:

    try:
        pId = str(sheet['B' + str(rowIndex)].value)
        pCount = int(sheet['D' + str(rowIndex)].value)
        pId2 = str(sheet['E' + str(rowIndex)].value)
        pCount2 = int(sheet['G' + str(rowIndex)].value)

        pBatchData[0].append({ "id": pId, "count": pCount })
        pBatchData[1].append({ "id": pId2, "count": pCount2 })
    except:
        pass
    finally:
        rowIndex += 1

print('Data: %s' % pBatchData)


boilerSState = ['E3', 'F3', 'G3', 'H3', 'I3', 'J3', 'K3', 'L3', 'M3', 'N3']
boilerEStateCount = ['E9', 'F9', 'G9', 'H9', 'I9', 'J9', 'K9', 'L9', 'M9', 'N9']

sheet = wb['配置']
for i in range(len(boilerSState)):
    try:
        boilerSState[i] = int(sheet[boilerSState[i]].value)
    except:
        boilerSState[i] = 0

for i in range(len(boilerEStateCount)):
    try:
        boilerEStateCount[i] = int(sheet[boilerEStateCount[i]].value)
    except:
        boilerEStateCount[i] = 0

# 合并第0&9圈数量
boilerEStateCount[0] += boilerEStateCount[9]
boilerEStateCount.pop()

print(str(boilerSState))
# 排程
schl = Schedule([5, 6])

schl.set_boiler_s_states(boilerSState)
schl.set_boiler_e_state_count(boilerEStateCount)
schl.schedule(pBatchData)
schl.print_schedule()
schl.verify()
schl.desperse()


# 输出排程数据
f = open('./static/js/data.js', mode='w', encoding='utf-8')
f.write('var SCHEMES_DATA = {')
f.write('\r\n\t\'boilerSStates\': ' + json.dumps(schl.get_boiler_s_states()) + ',')
f.write('\r\n\t\'boilerEStateCount\': ' + json.dumps(schl.get_boiler_e_state_count()) + ',')
f.write('\r\n\t\'productData\': ' + json.dumps(schl.get_product_data()))
f.write('\r\n};\r\n')
f.write('var SCHEDULE_DATA = ' + json.dumps(schl.get_schedule()) + ';')
print('保存成功。')
f.close()

# 打开视图
os.system('start "‪C:\\Program Files (x86)\\Maxthon5\\Bin\\Maxthon.exe" "D:\\PythonWorkspace\\juewei_pot_schedule\\static\\template.html"')



