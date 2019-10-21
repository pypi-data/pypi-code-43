from distutils.core import setup

setup(
  name = 'CoachCare',         # How you named your package folder (MyLib)
  packages = ['CoachCare'],   # Chose the same as "name"
  version = '0.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'seca CoachCare integration',   # Give a short description about your library
  author = 'Robert Martinez',                   # Type in your name
  author_email = 'robert.martinez@seca.com',      # Type in your E-Mail
  url = 'https://github.com/user/reponame',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['seca', 'coachcare', 'integration', 'mbca'],   # Keywords that define your package best
  install_requires=[            
          'Flask',
          'hl7apy',
          'psycopg2-binary',
          'requests'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.4', #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
