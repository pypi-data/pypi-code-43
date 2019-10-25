from setuptools import setup,find_packages

long_description = "" #这里可以导入外部的README.md

setup(
    name='marktex',
    version='0.7.8.5.dev1',
    description='convert markdown 2 latex code perfactly,support Chinese Language',
    long_description = long_description,
    url='https://github.com/sailist/MarkTex',
    author='hzYang',
    author_email='sailist@outlook.com',
    license='MIT',
    include_package_data = True,
    install_requires = [
      "pylatex",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='markdown latex convert',
    packages=find_packages(),
    entry_points={
        'console_scripts':[
            'marktex = marktex.marktex:main'
        ]
      },
)


import jieba
import os
import csv

List1 = []
List2 = []
List3 = []
for line in open('C:\\Users\\95338\\Desktop\\讯飞比赛\\大数据应用分类标注-选手\\apptype_train.txt', encoding='utf-8'):
    tmps = line.strip().split('\t')
    List1.append(tmps[0].encode(
        'utf-8').decode('utf-8-sig').strip().replace('。', ''))
    List2.append(tmps[1].encode(
        'utf-8').decode('utf-8-sig').strip().replace('。', ''))
    List3.append(tmps[2].encode(
        'utf-8').decode('utf-8-sig').strip().replace('。', ''))
print(List1)
print(List2)

current_dir = os.path.abspath('.')
file_name = os.path.join(current_dir, "C:\\Users\\95338\\Desktop\\讯飞比赛\\大数据应用分类标注-选手\\csv3.csv")
# csvfile = open(file_name, 'wt',encoding='gb18030')  #

with open(file_name,"w",encoding="utf-8") as w:
    header = ['appid', 'typeid', 'description']
    w.write("{},{},{}\n".format(header[0],header[1],header[2]))
    for a,b,c in zip(List1,List2,List3):
        w.write("{},{},{}\n".format(a,b,c))
#
# writer=csv.writer(csvfile)
# header=['appid','typeid','description']
#
#
# writer.writerow(header)
# writer.writerows(zip(List1,List2,List3))
# csvfile.close()
