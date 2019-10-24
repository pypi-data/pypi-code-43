from distutils.core import setup

setup(
  name = 'splus',         
  packages = ['splus'],   
  version = '0.1',      
  license='MIT',        
  description = 'SPLUS SDK',  
  author = 'Pankaj',                  
  url = 'https://github.com/pankajsa/splus/',   
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz', 
  keywords = ['SDK', 'PUBSUB'],   
  install_requires=[            # I get to this in a second
          'validators',
          'beautifulsoup4',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)