from setuptools import setup

# python setup.py sdist bdist_wheel
# twine upload dist/*

setup(name='generate_graphene',
      version='0.1.3',
      description='Generate Django-Graphene (graphql) queries and mutations for your Django models ',
      url='http://github.com/joeydebreuk/generate_graphene',
      author='Joey van Breukelen',
      author_email='jabreukelen@gmail.com',
      license='MIT',
      packages=['generate_graphene'],
      install_requires=[
          'graphene==2.1.7',
          'graphene-django==2.4.0',
          'graphene-django-extras==0.4.5',
          'graphql-core==2.2.1',
          'graphql-relay==2.0.0',
          'djangorestframework==3.10.2',
          'Django==2.2.3',
          'typedecorator==0.0.5',
      ],
      zip_safe=False
      )
