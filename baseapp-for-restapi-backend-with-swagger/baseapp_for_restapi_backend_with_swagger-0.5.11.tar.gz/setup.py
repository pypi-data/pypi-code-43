from setuptools import setup
import versioneer

#Dependancy lists maintained here and in tox.ini
sp_install_requires = [
  'pytz==2018.4',
  'flask==1.0.2',
  'flask_restplus==0.11.0',
  'python-dateutil==2.7.2',
  'sortedcontainers==1.5.9',
  'bcrypt==3.1.5',
  'pyjwt==1.7.1'
]
sp_tests_require = [
  'nose==1.3.7'
]

all_require = sp_install_requires + sp_tests_require

setup(name='baseapp_for_restapi_backend_with_swagger',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Python package which provides a base application class for an app with a restapi backend that provides a swagger',
      url='https://github.com/rmetcalf9/baseapp_for_restapi_backend_with_swagger',
      author='Robert Metcalf',
      author_email='rmetcalf9@googlemail.com',
      license='MIT',
      packages=['baseapp_for_restapi_backend_with_swagger'],
      zip_safe=False,
      install_requires=sp_install_requires,
      tests_require=sp_tests_require,
      include_package_data=True)
