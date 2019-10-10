# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dator', 'dator.datastorages', 'dator.transformers']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0',
 'carto>=1.4,<2.0',
 'cartoframes>=0.9.2,<0.10.0',
 'google-cloud-bigquery>=1.11,<2.0',
 'marshmallow>=2.19,<3.0',
 'numpy>=1.17,<2.0',
 'pandas>=0.24.2,<0.25.0',
 'psycopg2-binary>=2.8.2,<3.0.0',
 'sqlalchemy>=1.1.15,<2.0.0']

setup_kwargs = {
    'name': 'geolibs-dator',
    'version': '0.0.7',
    'description': 'GeoLibs Dator - A data extractor',
    'long_description': '# GeoLibs-Dator\nDator, a data extractor (ETL as a library), that uses Pandas\' DataFrames as in memory temporal storage.\n\n### Features\n| Source | Extract | Transform | Load |\n| --- | --- | --- | --- |\n| BigQuery | Y | Y |  |\n| CARTO | Y | Y | Y* |\n| CSV | Y |  | Y |\n| Pandas |  | Y |  |\n| PostgreSQL | Y | Y | Y |\n\n_* Note:_ We are waiting for the append feature on [CARTOframes](https://github.com/CartoDB/cartoframes), because the one we are using is a _ñapa_.\n\n### Configuration\nCreate a `config.yml` file using the `config.example.yml` one as guide. You can find in that one all the possible ETL cases.\n\nIf you are using BigQuery in your ETL process, you need to add a `GOOGLE_APPLICATION_CREDENTIALS` environment variable with the path to your Google Cloud\'s `credentials.json` file.\n\nYou can test them with the `example.py` file.\n\n#### Example\n\n*dator_config.yml*\n\n```yml\ndatastorages:\n  bigquery_input:\n    type: bigquery\n    data:\n      query: SELECT * FROM `dataset.table` WHERE updated_at >= \'2019-05-04T00:00:00Z\' AND updated_at < \'2019-06-01T00:00:00Z\';\n\n  carto_input:\n    type: carto\n    credentials:\n      url: https://domain.com/user/user/\n      api_key: api_key\n    data:\n      table: table\n\n  postgresql_input:\n    credentials:\n      ...\n    data:\n      query: SELECT * FROM somewhere;\n      types:\n        - name: timeinstant\n          type: datetime\n        - name: fillinglevel\n          type: float\n        - name: temperature\n          type: int\n        - name: category\n          type: str\n\n  carto_output:\n    type: carto\n    credentials:\n      url: https://domain.com/user/user/\n      api_key: api_key\n    data:\n      table: table\n      append: false\n\ntransformations:\n  bigquery_agg:\n    type: bigquery\n    time:\n      field: updated_at\n      start: "2019-05-02T00:00:00Z"  # As string or YAML will parse them as DateTimes\n      finish: "2019-05-03T00:00:00Z"\n      step: 5 MINUTE\n    aggregate:\n      by:\n        - container_id\n        - updated_at\n      fields:\n        field_0: avg\n        field_1: max\n\nextract: bigquery_input\ntransform: bigquery_agg\nload: carto_output\n```\n\n### How to use\n\nThis package is designed to accomplish ETL operations in three steps:\n\n#### Extract\n\nThe extract method is a default method, this means although this method can be overwritten, by default, it must work via config.\n\n(This section under construction)\n\n#### Transform\n\n(This section under construction)\n\n#### Load\n\nThe load method is a default method, this means although this method can be overwritten, by default, it must work via config. It can receive 2 parameters, the Pandas dataframe and a dictionary with extra info.\n\n#### Example\n\n*app.py*\n\n```python\nfrom dator import Dator\n\ndator = Dator(\'/usr/src/app/dator_config.yml\')\ndf = dator.extract()\ndf = dator.transform(df)\ndator.load(df)\n```\n\n*app.py* with extra info\n\n```python\nfrom dator import Dator\n\ndef upsert_method:\n  pass\n\ndator = Dator(\'/usr/src/app/dator_config.yml\')\ndf = dator.extract()\ndf = dator.transform(df)\ndator.load(df, {\'method\': upsert_method})\n```\n\n### TODOs\n- Better doc.\n- Tests.\n',
    'author': 'Geographica',
    'author_email': 'hello@geographica.com',
    'url': 'https://github.com/GeographicaGS/GeoLibs-Dator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
