from setuptools import find_packages, setup
setup(
    name='requestsModel',  # package
    version='2.1.1',
    description='requests_Model',
    long_description='args: get_response、get_resText、get_resText_cookies、get_resText_post、get_resText_post_cookies、parse_reg_info、get_cookie',
    author='donglidunyin',
    author_email='donglidunyin@163.com',
    install_requires=[
        'requests>=2.22.0',
        'retrying>=1.3.3',
    ],
    packages=find_packages(),
)
