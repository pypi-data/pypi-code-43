from setuptools import setup
import setuptools
setup(name='musket_ml',
      version='0.491',
      description='Common parts of my pipelines',
      url='https://github.com/petrochenko-pavel-a/musket_core',
      author='Petrochenko Pavel',
      author_email='petrochenko.pavel.a@gmail.com',
      license='MIT',
      packages=setuptools.find_packages(),
      include_package_data=True,
      install_requires=["musket_text>=0.43","musket_core>=0.49","classification_pipeline>=0.43","segmentation_pipeline>=0.43"],
      zip_safe=False)