from setuptools import setup, find_packages


setup(
    name='deeppages',
    version='0.2.4',
    description="Django's database stored web content processor",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ricardofalasca/deep-pages',
    author='Ricardo Falasca',
    author_email='ricardo@falasca.com.br',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        'django>1.10',
        'django-autoslug>=1.9.4',
    ]
)
