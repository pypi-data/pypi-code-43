# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='enhautocorrect',
    version='0.0.72',
    url='https://github.com/macalencar/enhautocorrect',
    license='MIT License',
    author='Márcio Alencar',
    author_email='macalencar@gmail.com',
    keywords=['autocorrect', 'spelling', 'corrector'],
    description='Enhancements in autocorrect library',
    package_data = {'enhautocorrect': ['data/*.*']},
    packages=['enhautocorrect'],
      #download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
    #install_requires=['validators', 'beautifulsoup4',],
    classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)

