from setuptools import setup
setup(
  name = 'autoD',         # How you named your package folder (MyLib)
  packages = ['autoD'],   # Chose the same as "name"
  version = '3.8.0',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Forward automatic differentiation',   # Give a short description about your library
  author = 'Wei Xuan Chan',                   # Type in your name
  author_email = 'w.x.chan1986@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/WeiXuanChan/autoD',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/WeiXuanChan/autoD/archive/v3.8.0.tar.gz',    # I explain this later on
  keywords = ['automatic', 'differentiation'],   # Keywords that define your package best
  install_requires=['numpy'],
          
  classifiers=[
    'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package    
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',    
    'License :: OSI Approved :: MIT License',   # Again, pick a license    
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
