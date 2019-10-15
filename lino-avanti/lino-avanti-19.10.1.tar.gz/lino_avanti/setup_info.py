# -*- coding: UTF-8 -*-
# test it with: $ python setup.py test -s tests.PackagesTests
# Copyright 2017-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
SETUP_INFO = dict(
    name='lino-avanti',
    version='19.10.1',
    install_requires=['lino-xl', 'metafone'],
    description=("Manage the integration course of immigrants in East Belgium"),
    author='Luc Saffre',
    author_email='luc.saffre@gmail.com',
    url="http://avanti.lino-framework.org/",
    license='BSD-2-Clause',
    test_suite='tests')


SETUP_INFO.update(long_description=u"""
Lino Avanti is a free `Lino <http://www.lino-framework.org/>`__
application used by social workers in East Belgium for helping
immigrants with their *integration course*.

The **integration course** is a Belgian administrative procedure
consisting in an individual mentoring and a series of courses with the
goal of helping new residents to acquire the base knowledge about
society and social relations in Belgium in order to ease their
integration on the territory.  Read more about the procedure in
`Parcours d’intégration des primo-arrivants
<http://socialsante.wallonie.be/?q=action-sociale/integration-personne-origine-etrangere/dispositifs/parcours-integration-primo-arrivant>`__
(French) or `Integrationsparcours: Der Einstiegsweg für Migranten
<http://www.dglive.be/desktopdefault.aspx/tabid-4795/8506_read-47195/>`__
(German).

Lino Avanti is being developed by order of `Ministerium der
Deutschsprachigen Gemeinschaft <http://www.dglive.be>`__ (Ministery of
the `German-speaking Community of Belgium
<https://en.wikipedia.org/wiki/German-speaking_Community_of_Belgium>`__).
""")

SETUP_INFO.update(classifiers="""
Programming Language :: Python
Programming Language :: Python :: 3
Development Status :: 5 - Production/Stable
Environment :: Web Environment
Framework :: Django
Intended Audience :: Developers
Intended Audience :: System Administrators
Intended Audience :: Information Technology
Intended Audience :: Customer Service
License :: OSI Approved :: BSD License
Natural Language :: English
Natural Language :: German
Natural Language :: French
Operating System :: OS Independent
Topic :: Office/Business :: Scheduling
""".format(**SETUP_INFO).strip().splitlines())
SETUP_INFO.update(packages=[
    'lino_avanti',
    'lino_avanti.lib',
    'lino_avanti.lib.avanti',
    'lino_avanti.lib.avanti.fixtures',
    'lino_avanti.lib.cal',
    'lino_avanti.lib.cal.fixtures',
    'lino_avanti.lib.contacts',
    'lino_avanti.lib.contacts.fixtures',
    'lino_avanti.lib.contacts.management',
    'lino_avanti.lib.cv',
    'lino_avanti.lib.cv.fixtures',
    'lino_avanti.lib.contacts.management.commands',
    'lino_avanti.lib.courses',
    'lino_avanti.lib.households',
    'lino_avanti.lib.households.fixtures',
    'lino_avanti.lib.tickets',
    'lino_avanti.lib.users',
    'lino_avanti.lib.users.fixtures'
])

SETUP_INFO.update(message_extractors={
    'lino_avanti': [
        ('**/cache/**', 'ignore', None),
        ('**.py', 'python', None),
        ('**.js', 'javascript', None),
        ('**/config/**.html', 'jinja2', None),
    ],
})

SETUP_INFO.update(include_package_data=True)


# def add_package_data(package, *patterns):
#     l = SETUP_INFO['package_data'].setdefault(package, [])
#     l.extend(patterns)
#     return l
#
# l = add_package_data('lino_avanti.lib.avanti')
# for lng in 'de fr'.split():
#     l.append('locale/%s/LC_MESSAGES/*.mo' % lng)
