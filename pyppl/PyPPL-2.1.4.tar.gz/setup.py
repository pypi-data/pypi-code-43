# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyppl']

package_data = \
{'': ['*']}

install_requires = \
['cmdy',
 'colorama>=0.4.1,<0.5.0',
 'filelock>=3.0.0,<4.0.0',
 'liquidpy',
 'pluggy>=0.12,<0.13',
 'psutil>=5.6,<6.0',
 'pyparam',
 'pyppl_flowchart',
 'pyppl_report',
 'python-box87',
 'python-simpleconf',
 'transitions>=0.6.0,<0.7.0']

entry_points = \
{'console_scripts': ['pyppl = pyppl.console:main']}

setup_kwargs = {
    'name': 'pyppl',
    'version': '2.1.4',
    'description': 'A Python PiPeLine framework',
    'long_description': '# [PyPPL][3] - A [Py](#)thon [P](#)i[P](#)e[L](#)ine framework\n\n[![Pypi][10]][18] [![Github][11]][3] [![PythonVers][14]][18] [![docs][19]][1] [![Travis building][5]][7] [![Codacy][4]][8] [![Codacy coverage][6]][8]\n\n[Documentation][1] | [API][2] | [Change log][9]\n\n<!-- toc -->\n## Features\n- Process caching.\n- Process reusability.\n- Process error handling.\n- Runner customization.\n- Running profile switching.\n- Plugin system.\n- Pipeline flowchart (using plugin [pyppl_flowchart][22]).\n- Pipeline report (using plugin [pyppl_report][23]).\n\n## Installation\n```bash\npip install PyPPL\n```\n\n## Writing pipelines with predefined processes\nLet\'s say we are implementing the [TCGA DNA-Seq Re-alignment Workflow][16]\n(The very left part of following figure).\nFor demonstration, we will skip the QC and the co-clean parts here.\n\n[![DNA_Seq_Variant_Calling_Pipeline][15]][16]\n\n`demo.py`:\n```python\nfrom pyppl import PyPPL, Channel\n# import predefined processes\nfrom TCGAprocs import pBamToFastq, pAlignment, pBamSort, pBamMerge, pMarkDups\n\n# Load the bam files\npBamToFastq.input = Channel.fromPattern(\'/path/to/*.bam\')\n# Align the reads to reference genome\npAlignment.depends = pBamToFastq\n# Sort bam files\npBamSort.depends = pAlignment\n# Merge bam files\npBamMerge.depends = pBamSort\n# Mark duplicates\npMarkDups.depends = pBamMerge\n# Export the results\npMarkDups.exdir = \'/path/to/realigned_Bams\'\n# Specify the start process and run the pipeline\nPyPPL().start(pBamToFastq).run()\n```\n\n[![asciicast][20]][21]\n\n## Implementing individual processes\n`TCGAprocs.py`:\n```python\nfrom pyppl import Proc\npBamToFastq = Proc(desc = \'Convert bam files to fastq files.\')\npBamToFastq.input = \'infile:file\'\npBamToFastq.output = [\n    \'fq1:file:{{i.infile | stem}}_1.fq.gz\',\n    \'fq2:file:{{i.infile | stem}}_2.fq.gz\']\npBamToFastq.script = \'\'\'\nbamtofastq collate=1 exclude=QCFAIL,SECONDARY,SUPPLEMENTARY \\\n    filename= {{i.infile}} gz=1 inputformat=bam level=5 \\\n    outputdir= {{job.outdir}} outputperreadgroup=1 tryoq=1 \\\n    outputperreadgroupsuffixF=_1.fq.gz \\\n    outputperreadgroupsuffixF2=_2.fq.gz \\\n    outputperreadgroupsuffixO=_o1.fq.gz \\\n    outputperreadgroupsuffixO2=_o2.fq.gz \\\n    outputperreadgroupsuffixS=_s.fq.gz\n\'\'\'\n\npAlignment = Proc(desc = \'Align reads to reference genome.\')\npAlignment.input = \'fq1:file, fq2:file\'\n#                             name_1.fq.gz => name.bam\npAlignment.output = \'bam:file:{{i.fq1 | stem | stem | [:-2]}}.bam\'\npAlignment.script = \'\'\'\nbwa mem -t 8 -T 0 -R <read_group> <reference> {{i.fq1}} {{i.fq2}} | \\\n    samtools view -Shb -o {{o.bam}} -\n\'\'\'\n\npBamSort = Proc(desc = \'Sort bam files.\')\npBamSort.input = \'inbam:file\'\npBamSort.output = \'outbam:file:{{i.inbam | basename}}\'\npBamSort.script = \'\'\'\njava -jar picard.jar SortSam CREATE_INDEX=true INPUT={{i.inbam}} \\\n    OUTPUT={{o.outbam}} SORT_ORDER=coordinate VALIDATION_STRINGENCY=STRICT\n\'\'\'\n\npBamMerge = Proc(desc = \'Merge bam files.\')\npBamMerge.input = \'inbam:file\'\npBamMerge.output = \'outbam:file:{{i.inbam | basename}}\'\npBamMerge.script = \'\'\'\njava -jar picard.jar MergeSamFiles ASSUME_SORTED=false CREATE_INDEX=true \\\n    INPUT={{i.inbam}} MERGE_SEQUENCE_DICTIONARIES=false OUTPUT={{o.outbam}} \\\n    SORT_ORDER=coordinate USE_THREADING=true VALIDATION_STRINGENCY=STRICT\n\'\'\'\n\npMarkDups = Proc(desc = \'Mark duplicates.\')\npMarkDups.input = \'inbam:file\'\npMarkDups.output = \'outbam:file:{{i.inbam | basename}}\'\npMarkDups.script = \'\'\'\njava -jar picard.jar MarkDuplicates CREATE_INDEX=true INPUT={{i.inbam}} \\\n    OUTPUT={{o.outbam}} VALIDATION_STRINGENCY=STRICT\n\'\'\'\n```\n\nEach process is indenpendent so that you may also reuse the processes in other pipelines.\n\n## Pipeline flowchart\n```python\n# When try to run your pipline, instead of:\n#   PyPPL().start(pBamToFastq).run()\n# do:\nPyPPL().start(pBamToFastq).flowchart().run()\n```\nThen an SVG file endswith `.pyppl.svg` will be generated under current directory.\nNote that this function requires [Graphviz][13] and [graphviz for python][12].\n\nSee plugin [details][22].\n\n![flowchart][17]\n\n## Pipeline report\nSee plugin [details][23]\n\n````python\npPyClone.report = """\n## {{title}}\n\nPyClone[1] is a tool using Probabilistic model for inferring clonal population structure from deep NGS sequencing.\n\n![Similarity matrix]({{path.join(job.o.outdir, "plots/loci/similarity_matrix.svg")}})\n\n```table\ncaption: Clusters\nfile: "{{path.join(job.o.outdir, "tables/cluster.tsv")}}"\nrows: 10\n```\n\n[1]: Roth, Andrew, et al. "PyClone: statistical inference of clonal population structure in cancer." Nature methods 11.4 (2014): 396.\n"""\n\n# or use a template file\n\npPyClone.report = "file:/path/to/template.md"\n````\n\n```python\nPyPPL().start(pPyClone).run().report(\'/path/to/report\', title = \'Clonality analysis using PyClone\')\n```\n\n![report][24]\n\n## Full documentation\n[ReadTheDocs][1]\n\n\n[1]: https://pyppl.readthedocs.io/en/latest/\n[2]: https://pyppl.readthedocs.io/en/latest/api/\n[3]: https://github.com/pwwang/pyppl/\n[4]: https://img.shields.io/codacy/grade/a04aac445f384a8dbe47da19c779763f.svg?style=flat-square\n[5]: https://img.shields.io/travis/pwwang/PyPPL.svg?style=flat-square\n[6]: https://img.shields.io/codacy/coverage/a04aac445f384a8dbe47da19c779763f.svg?style=flat-square\n[7]: https://travis-ci.org/pwwang/PyPPL\n[8]: https://app.codacy.com/project/pwwang/PyPPL/dashboard\n[9]: https://pyppl.readthedocs.io/en/latest/CHANGELOG/\n[10]: https://img.shields.io/pypi/v/pyppl.svg?style=flat-square\n[11]: https://img.shields.io/github/tag/pwwang/PyPPL.svg?style=flat-square\n[12]: https://github.com/xflr6/graphviz\n[13]: https://www.graphviz.org/\n[14]: https://img.shields.io/pypi/pyversions/PyPPL.svg?style=flat-square\n[15]: https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/images/dna-alignment-pipeline_0.png\n[16]: https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/DNA_Seq_Variant_Calling_Pipeline/\n[17]: https://raw.githubusercontent.com/pwwang/PyPPL/development/examples/demo/demo.pyppl.svg?sanitize=true\n[18]: https://pypi.org/project/PyPPL/\n[19]: https://img.shields.io/readthedocs/pyppl.svg?style=flat-square\n[20]: https://asciinema.org/a/Uiz6Wdo1buGCGPFd89bWiZzwn.svg?sanitize=true\n[21]: https://asciinema.org/a/Uiz6Wdo1buGCGPFd89bWiZzwn\n[22]: https://github.com/pwwang/pyppl_flowchart\n[23]: https://github.com/pwwang/pyppl_report\n[24]: https://pyppl_report.readthedocs.io/en/latest/snapshot.png\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'url': 'https://github.com/pwwang/PyPPL',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
