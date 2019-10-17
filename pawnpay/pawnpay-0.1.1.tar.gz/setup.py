from setuptools import setup

setup(name='pawnpay',
      version='0.1.1',
      description='The official Python client library for the Pawn Payment Solutions API',
      keywords=['pawn', 'pay', 'pawn-pay', 'client', 'pawnmaster', 'pawndex', 'api'],
      url='https://pawn-pay.com',
      author='Pawn Payment Solutions',
      author_email='support@pawn-pay.com',
      license='GNUv3',
      packages=['pawn_pay', 'pawn_pay.helpers', 'pawn_pay.PawnMaster', 'pawn_pay.PawnDex'],
      install_requires=['sentry_sdk', 'loguru', 'requests', 'ratelimit', 'sqlalchemy', 'Cython', 'pymssql', 'pyodbc', 'fuzzywuzzy', 'python-Levenshtein-wheels', 'yaspin'],
      zip_safe=False)