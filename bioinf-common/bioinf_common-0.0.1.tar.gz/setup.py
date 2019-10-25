from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext


# extension definitions
DEBUG = True
ext_args = dict(
    extra_compile_args=['-std=c++14'],
    undef_macros=['NDEBUG'] if DEBUG else []
)

nc_module = Extension(
    'bioinf_common.algorithms.network_coherence_cpp',
    sources=[
        'bioinf_common/tools/cpp_utils.cpp',
        'bioinf_common/algorithms/network_coherence_cpp.cpp'
    ],
    **ext_args
)

cs_module = Extension(
    'bioinf_common.algorithms.cluster_separation_cpp',
    sources=[
        'bioinf_common/tools/cpp_utils.cpp',
        'bioinf_common/algorithms/cluster_separation_cpp.cpp'
    ],
    **ext_args
)

utils_module = Extension(
    'bioinf_common.tools.cpp_utils',
    sources=['bioinf_common/tools/cpp_utils.cpp'],
    libraries=[
        'armadillo'
    ],
    **ext_args
)


class BuildExt(build_ext):
    def build_extensions(self):
        # import pybind11
        # for ext in self.extensions:
        #     ext.include_dirs.extend([
        #         pybind11.get_include(),
        #         pybind11.get_include(True)
        #     ])

        build_ext.build_extensions(self)


# setup project
setup(
    name='bioinf_common',
    version='0.0.1',

    description='Aggregation of functionalities needed in multiple projects',

    author='kpj',
    author_email='kpjkpjkpjkpjkpjkpj@gmail.com',

    packages=find_packages(exclude=['tests']),

    install_requires=[
        'numpy', 'pandas', 'networkx', 'dask[complete]',
        'scipy', 'statsmodels', 'gene_map', 'obonet',
        'tqdm', 'joblib', 'bs4', 'jupyter', 'click', 'psutil',
        'pybind11'
    ],

    scripts=['bin/exec_ipynb', 'bin/watch_process'],
    ext_modules=[utils_module, nc_module, cs_module],
    cmdclass={'build_ext': BuildExt}
)
