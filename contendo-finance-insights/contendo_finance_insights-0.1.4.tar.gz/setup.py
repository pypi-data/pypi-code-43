from setuptools import setup

setup(name='contendo_finance_insights',
    version='0.1.4',
    description='contendo.ai finance insights package',
    url='https://github.com/Yahalis/contendo_finance/tree/master/finance_insights',
    author='Yahali Sherman, contendo.ai',
    author_email='yahali@contendo.ai',
    license='APACHE2',
    packages=['contendo_finance_insights'],
    install_requires=[
        'contendo_utils',
        'ta',
        'statsmodels',
        'newspaper3k',
        'nltk',
        'google-cloud-bigquery',
        'google-cloud-storage',
    ],
    zip_safe=False)
