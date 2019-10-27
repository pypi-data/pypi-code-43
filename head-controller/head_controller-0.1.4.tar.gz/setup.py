from setuptools import setup

setup(
    name='head_controller',
    packages=['head_controller'],
    description='A package to quickly train and predict head gestures',
    version='0.1.4',
    url = 'https://github.com/nightvision04/simple-gesture-tracking',
    author='Dan Scott',
    author_email='danscottlearns@gmail.com',
    keywords=['head','controller','nueral net','movement','axis','recognition','computer vision','head tracking'],
    install_requires=[
          'opencv-python',
          'mysqlclient',
          'pymysql',
          'sklearn'
      ],
      classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7',
  ],
    )
