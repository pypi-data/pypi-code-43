import io
import json
import subprocess
import sys

from isc_common import getAttr


def makeInfo():
    data = json.loads(io.open('./package.json', encoding='utf-8').read())

    info = []
    info.append(dict(libName='Разработка :', libVersion='"АО ИВЦ \"Информ\" (info@ivc-inform.ru)'))
    info.append(dict(libName='Версия :', libVersion=getAttr(data, 'version')))
    info.append(dict(libName='Авторы :', libVersion=getAttr(data, 'author')))
    info.append(dict(libName='Контакты :', libVersion="+7 (495) 997-91-75"))

    installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages_list = sorted([(item[: item.find('==')], item[item.find('==') + 2:]) for item in
                                      installed_packages.decode("utf-8").split('\n')])

    for (libName, libVersion) in installed_packages_list:
        info.append(dict(libName=libName, libVersion=libVersion))

    file = open('MakeAboutData.js', 'w')
    str = f"simpleSyS.aboutData = {json.dumps(info)}"
    file.write(str)
    file.close()
