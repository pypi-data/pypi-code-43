SETUP_INFO = dict(
    name='getlino',
    version='19.10.4',
    install_requires=['setuptools', 'click', 'virtualenv', 'jinja2', 'atelier'],
    test_suite='tests',
    description="Lino installer",
    long_description="""
A tool to install and configure Lino in different environments.

The central project homepage is http://getlino.lino-framework.org

    """,
    author='Rumma & Ko Ltd',
    author_email='team@lino-framework.org',
    url="http://getlino.lino-framework.org",
    license='BSD-2-Clause',
    entry_points={
        'console_scripts': ['getlino = getlino.cli:main']
    },

    classifiers="""\
Programming Language :: Python :: 3
Development Status :: 4 - Beta
Environment :: Console
Framework :: Django
Intended Audience :: Developers
Intended Audience :: System Administrators
License :: OSI Approved :: BSD License
Operating System :: OS Independent
Topic :: System :: Installation/Setup
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines())

SETUP_INFO.update(
    zip_safe=False,
    include_package_data=True)

SETUP_INFO.update(packages=[n for n in """
getlino
""".splitlines() if n])
