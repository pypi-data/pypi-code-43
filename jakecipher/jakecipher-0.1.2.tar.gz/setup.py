from setuptools import setup

'''
LOCAL: 
install:  pip install .

---------------------------------------
REMOTE:
pip install --user --upgrade twine

## upload
python setup.py sdist bdist_wheel
# test : https://test.pypi.org/project/mypackcrazyj/
python -m twine upload -u crazyj --repository-url https://test.pypi.org/legacy/ dist/* --verbose

## install
pip install --upgrade --index-url https://test.pypi.org/simple/ --no-deps jakecipher
pip uninstall mpackcrazyj

## RELEASE
# release : https://pypi.org/project/mypackcrazyj
python -m twine upload -u crazyj dist/* --verbose
pip install mypackcrazyj
 

'''
import setuptools

with open("README.md", "r", encoding="utf8") as f:
      long_description = f.read()

# version 수정시 _init_에서도 version 수정해야 함.
setup(
      name='jakecipher',
      version='0.1.2',
      description='jake cipher algorithm',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/crazyj7/pythonpack/tree/master/jakecipher',

      author='crazyj',
      author_email='crazyj7@gmail.com',
      license='MIT',

      packages=setuptools.find_packages(),
      install_requires=['numpy',],
      zip_safe=False,
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      python_requires = '>=3.6',
)


'''

install_requires : import files...
python_requires='>=3.6'


'''