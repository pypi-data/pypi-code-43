from setuptools import setup

setup(
 name='tmrevpviz',
 version='1.2.3',
 license='MIT',
 packages=[],
 package_dir={'' : 'src'},
 entry_points={
    'console_scripts': [
        'tmrevpviz-run=tmrevpviz:run'
    ]
},
 py_modules=['tmrevpviz', 'Incident'],
 classifiers=[
      'Environment :: Console',
      'Operating System :: Microsoft :: Windows',
      'Programming Language :: Python',
  ],
  install_requires=['datetime',
                    'matplotlib',
                    'numpy',
                    'pandas',
                    'statistics',
                    'xlsxwriter']
)
