from setuptools import setup

setup(
    name='head_controller',
    packages=['head_controller'],
    description='A package to learn and understand 2 axis head movements',
    version='0.1.1',
    url = 'https://github.com/nightvision04/simple-gesture-tracking',
    author='Dan Scott',
    author_email='danscottlearns@gmail.com',
    keywords=['head','controller','nueral net','movement','axis','recognition'],
    install_requires=[
          'opencv-python',
          'mysqlclient',
          'pymysql',
          'sklearn'
      ],
      classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.7',
  ],
    )
