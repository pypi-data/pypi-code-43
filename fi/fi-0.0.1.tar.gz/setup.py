from setuptools import setup

def get_version_from_file():
      with open('VERSION.txt', 'r') as version_file:
            tag = version_file.read()
      return tag


setup(name='fi',
      version=get_version_from_file(),
      description='The file open library the government doesn\'t want you to know about',
      url='https://github.com/python-efficiency/fi',
      author='python-efficiency',
      author_email='fi.pythonefficiency@gmail.com',
      license='MIT',
      packages=['fi'],
      install_requires=[],
      python_requires='>=3.5',
      zip_safe=False)