from setuptools import setup

setup(
    name='flask-task',
    version='1.0',
    url='https://github.com/FranciscoCarbonell/flask-task',
    license='MIT',
    author='Francisco Carbonell',
    author_email='francabezo@gmail.com',
    description='Basic flask task',
    py_modules=['flask_task'],
    zip_safe=False,
    include_package_data=False,
    platforms='any',
    install_requires=['Flask']
)