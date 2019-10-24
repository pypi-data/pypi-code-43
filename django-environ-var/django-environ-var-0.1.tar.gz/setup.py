from setuptools import setup
install_requires = [
      'django'
];
setup(name='django-environ-var',
      version='0.1',
      description='Declare Environment To Django Project',
      url='https://github.com/datasik/django-environ-var',
      author='Monirul Hasan',
      author_email='89monirulhasan@gmail.com',
      license='GPL',
      packages=['django_environ_var'],
      zip_safe=False)