# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cgranges', 'indextools', 'indextools.console']

package_data = \
{'': ['*'],
 'cgranges': ['cpp/*',
              'python/*',
              'test/*',
              'test/3rd-party/*',
              'test/3rd-party/AIList/*',
              'test/3rd-party/AITree/*',
              'test/3rd-party/NCList/*',
              'test/bedcov-cr.dSYM/Contents/*',
              'test/bedcov-cr.dSYM/Contents/Resources/DWARF/*',
              'test/bedcov-iitree.dSYM/Contents/*',
              'test/bedcov-iitree.dSYM/Contents/Resources/DWARF/*']}

install_requires = \
['autoclick>=0.6.1,<0.7.0',
 'loguru>=0.3.2,<0.4.0',
 'ngsindex>=0.1.7,<0.2.0',
 'pysam>=0.15,<0.16',
 'xphyle>=4.1.3,<5.0.0']

entry_points = \
{'console_scripts': ['indextools = indextools.console:indextools']}

setup_kwargs = {
    'name': 'indextools',
    'version': '0.1.4',
    'description': 'A toolkit for accelerating genomics using index files.',
    'long_description': '# IndexTools\n\nCommon index formats, such as BAM Index (BAI) and Tabix (TBI), contain coarse-grained information on the density of NGS reads along the genome that may be leveraged for rapid approximation of read depth-based metrics. IndexTools is a toolkit for extremely fast NGS analysis based on index files.\n\n## Installation\n\n### Pre-requisites\n\n* Python 3.6+\n\n### Pip\n\n```bash\npip install indextools\n```\n\n### From source\n\n* Clone the repository\n  ```\n  git clone https://github.com/dnanexus/IndexTools.git\n  ```\n* You\'ll need several tools to run the full install and release process\n    * [git](https://git-scm.com/)\n    * [curl](https://curl.haxx.se/)\n    * [make](https://www.gnu.org/software/make/)\n    * [Poetry](https://github.com/sdispater/poetry)\n    * [Black](https://github.com/python/black)\n    * [Flake8](http://flake8.pycqa.org/en/latest/)\n    * [Dunamai](https://github.com/mtkennerly/dunamai)\n* Then\n  ```bash\n  # Install locally\n  $ make install\n  # Release new version (if you are a maintainer)\n  $ make release version=<new version> token=<GitHub API Token>\n  ```\n\n## Commands\n\n### Partition\n\nThe `partition` command processes a BAM index file and generates a file in BED format that contains intervals that are roughly equal in "[volume](#volume)." This partition BAM file can be used for more efficient parallelization of secondary analysis tools (as opposed to parallelizing by chromosome or by uniform windows).\n\n```bash\n# Generate a BED with 10 partitions\nindextools partition -I tests/data/small.bam.bai \\\n  -z tests/data/contig_sizes.txt \\\n  -n 10 \\\n  -o small.partitions.bed\n```\n\n## Limitations\n\nIndexTools is under active development. Please see the [issue tracker](https://github.com/dnanexus/IndexTools/issues) and [road map](https://github.com/dnanexus/IndexTools/projects/1) to view upcoming features.\n\nSome of the most commonly requested features that are not yet available are:\n\n* Support for CRAM files and CRAM indexes (.crai).\n* Support for non-local files, via URIs.\n\n## Development\n\nWe welcome contributions from the community. Please see the [developer README](https://github.com/dnanexus/IndexTools/blob/develop/CONTRIBUTING.md) for details.\n\nContributors are required to abide by our [Code of Conduct](https://github.com/dnanexus/IndexTools/blob/develop/CODE_OF_CONDUCT.md).\n\n## Technical details\n\n### Volume\n\nIn a bioinformatics context, the term “size” is overloaded. It is used to refer to the linear size of a genomic region (number of bp), disk size (number of bytes), or number of features (e.g. read count). IndexTools estimates the approximate number of bytes required to store the uncompressed data of features within a given genomic region. To avoid confusion or conflation with any of the meanings of “size,” we chose instead to use the term “volume” to refer to the approximate size (in bytes) of a given genomic region. It is almost never important or useful to be able to interpret the meaning of a given volume, nor can volume be meaningfully translated to other units; volume is primarily useful as a relative measure. Thus, we use the made-up unit “V” when referring to any specific volume.\n\n## License\n\nIndexTools is Copyright (c) 2019 DNAnexus, Inc.; and is made available under the [MIT License](https://github.com/dnanexus/IndexTools/blob/develop/LICENSE).\n\nIndexTools is *not* an officially supported DNAnexus product. All bug reports and feature requests should be handled via the [issue tracker](https://github.com/dnanexus/IndexTools/issues). Please *do not* contact DNAnexus support regarding this software.\n\n## Acknowledgements\n\n* The initial inspiration for IndexTools came from @brentp\'s [indexcov](https://github.com/brentp/goleft/tree/master/indexcov).\n* IndexTools is built on several open-source libraries; see the [pyproject.toml](https://github.com/dnanexus/IndexTools/blob/develop/pyproject.toml) file for a full list.\n',
    'author': 'John Didion',
    'author_email': 'jdidion@dnanexus.com',
    'url': 'https://github.com/dnanexus/indextools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
