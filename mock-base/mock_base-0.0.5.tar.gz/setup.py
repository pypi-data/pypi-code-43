from setuptools import setup

setup(
    name='mock_base',
    version='0.0.5',
    description='mock for firebase_admin',
    author='Spina Nico',
    author_email='spinanico93@gmail.com',
    url='https://github.com/SpinaNico/python-mock-base',
    packages=[
        "mock_base",
        "mock_base._firestore",
        "mock_base._messaging"
    ],
    install_requires=[]
)