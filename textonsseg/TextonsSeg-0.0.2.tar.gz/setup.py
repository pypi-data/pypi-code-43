from distutils.core import setup
setup(
  name = 'TextonsSeg',         # How you named your package folder (MyLib)
  packages = ['TextonsSeg'],   # Chose the same as "name"
  version = '0.0.2',      # Start with a small number and increase it with every change you make
  license='gpl-3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Unsupervised image segmentatoin based on shape filters',   # Give a short description about your library
  author = 'Aditya Kishore',                   # Type in your name
  author_email = 'aditya20kishore@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/BATspock/TextonsSeg',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/BATspock/TextonsSeg/archive/v0.0.2.tar.gz',    # I explain this later on
  keywords = ['Unsupervised Machine learning', 'Textons'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
          'opencv-python',
          'scikit-learn',
        ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',   # Again, pick a license
    'Programming Language :: Python :: 3.7',      #Specify which pyhton versions that you want to support

  ],
)