from setuptools import setup, find_packages

setup(
    name="jieba-calcu",
    packages=find_packages(),
    version='1.0.7',
    description="word discovery",
    author="QinHaiNing",
    author_email='qinhaining@ultrapower.com.cn',
    url="",
    download_url='',
    keywords=['command', 'line', 'tool'],
    classifiers=[],
    entry_points={
        'console_scripts': [
        'command1 = advisorhelper.cmdline:execute',
        'command2 = adviserserver.create_algorithm:run',
        'command3 = adviserserver.run_algorithm:run'
        ]
    },
    install_requires=[
        'tqdm',
        'PyHamcrest',
        'twisted',
        'jieba',
        'numpy',
        'requests',
    ]
)
