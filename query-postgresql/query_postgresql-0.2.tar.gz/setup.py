from distutils.core import setup
setup(
  name = 'query_postgresql',         
  packages = ['query_postgresql'],   
  version = '0.2',      
  license='MIT',        
  description = 'Querying using Postgresql made easy',   
  author = 'Reza',                   
  author_email = 'reza16.sugiarto@gmail.com',      
  url = 'http://github.com/rezasugiarto/query_postgresql',   
  download_url = 'https://github.com/rezasugiarto/query_postgresql/archive/0.2.tar.gz',    
  keywords = ['postgresql'],   
  install_requires=[           
          'pandas',
          'psycopg2',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
