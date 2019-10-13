from setuptools import setup, find_packages

setup(name='VIGA',
      version='1.0',
      description='Vk information gathering api',
      author='Red',
      author_email='red.develop11@gmail.com',
      url='https://github.com/simplenikname/viga',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'tqdm',
          'requests',
          'bs4'
      ],
      include_package_data=True,
      zip_safe=False)
