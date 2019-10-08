from setuptools import setup, find_packages


setup(name='csf_kit',
      version='0.1.4',
      description='StartKit for ChinaScope data',
      author='ChinaScope',
      url='https://pypi.org/project/csf-kit/',
      author_email='song.lu@chinascope.com',
      packages=find_packages(),
      include_package_data=True,
      exclude_package_data={'': ['.gitignore']},
      install_requires=[
            'pandas',
            'numpy',
            'zipfile37',
            'python-dateutil',
            'alphalens'
      ]
      )
