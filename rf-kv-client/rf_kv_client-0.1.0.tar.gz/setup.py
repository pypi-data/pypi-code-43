from setuptools import setup, find_packages


setup(name='rf_kv_client',
      version='0.1.0',
      description='RedForester bindings for AcapellaDB',
      classifiers=[
                'Development Status :: 3 - Alpha',
                'License :: OSI Approved :: MIT License',
                'Programming Language :: Python :: 3.6',
            ],
      url='https://redforester.com',
      author='Red Forester',
      author_email='tech@redforester.com',
      license='MIT',
      packages=find_packages(),
      python_requires='>=3',
      install_requires=[
            'python-dateutil>=2.7.5',
            'acapelladb>=0.3.7'
      ],
      include_package_data=True,
      zip_safe=False
)
