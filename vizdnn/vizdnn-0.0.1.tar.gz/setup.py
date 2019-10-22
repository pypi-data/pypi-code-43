from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='vizdnn',
      version='0.0.1',
      description='Deep Neural Network Vizualizer',
      long_description= long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/karthikziffer/vizdnn',
      author='Karthik',
      author_email='karthik.cool1300@gmail.com',
      license='MIT',
      packages=['vizdnn'],
      install_requires=[
          'keras','matplotlib','numpy'
      ],
      zip_safe=False)