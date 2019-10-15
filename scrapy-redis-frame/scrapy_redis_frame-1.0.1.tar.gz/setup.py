import setuptools

setuptools.setup(
    name="scrapy_redis_frame",
    version="1.0.1",
    py_modules=['create_command'],
    author="SilenceSmile",
    author_email="845666796@qq.com",
    description="Scrapy Redis Util Package",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Click',
        'scrapy'
    ],
    entry_points={
        'console_scripts': ['scrapy_redis_create = scrapy_redis_frame.create_command:create_project']
    }
)