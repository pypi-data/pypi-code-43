"""
Flask-Envs
----------

Environment tools and configuration for Flask applications

Resources
`````````

- `Code & Documentation <http://github.com/jonaphin/flask-envs/>`_

"""
from setuptools import setup

setup(
    name='Flask-Envs',
    version='0.1.1',
    url='http://packages.python.org/flask-envs/',
    license='MIT',
    author='Jonathan Lancar',
    author_email='jonaphin@gmail.com',
    description='Environment tools and configuration for Flask applications',
    long_description=__doc__,
    py_modules=['flask_envs'],
    zip_safe=False,
    platforms='any',
    install_requires=['Flask', 'pyyaml'],
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
