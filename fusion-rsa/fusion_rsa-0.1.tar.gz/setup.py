from setuptools import setup

setup(name='fusion_rsa',
      version='0.1',
      description='Python library to compute RDMs from multiple sources.',
      keywords=["representation similarity analysis", "representational dissimilarity matrix"],
      url='https://github.com/haideraltahan/fusion_rsa',
      author='Haider Al-Tahan',
      author_email='haideraltahan@gmail.com',
      download_url='https://github.com/haideraltahan/fusion_rsa/archive/0.1.tar.gz',
      license='MIT',
      packages=['fusion_rsa'],
      python_requires='>=3.5',
      platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
      zip_safe=False,
      project_urls={
          "Bug Tracker": "https://bugs.example.com/HelloWorld/",
          "Documentation": "https://docs.example.com/HelloWorld/",
          "Source Code": "https://code.example.com/HelloWorld/",
      },
      install_requires=[
          'numpy'
      ],
      test_suite='nose.collector',
      tests_require=[
          'nose',
          'sphinx'
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      )
