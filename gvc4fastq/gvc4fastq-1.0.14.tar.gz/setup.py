# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages
import os


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
setup(
    name='gvc4fastq',     # 包名字
    version='1.0.14',   # 包版本
    python_requires="<3",
    description='GVC4FASTQ is a data processing pipeline developed by Genome Wisdom Inc. GVC4FASTQ detects germline and somatic mutations (SNV, InDel, SV) from FASTQ files.',   # 简单描述
    author='LongHui.Yin',  # 作者
    author_email='dragonfly.yin@genowis.com',  # 作者邮箱
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),                 # 包
    install_requires=['gvc4bam>=1.0.8','docker==2.5.1', 'pysam', 'toil', 'toil-runner'],
    classifiers=['Programming Language :: Python :: 2.7','License :: Free For Educational Use'],
    scripts=['tools/fastq_vcf.py','tools/check_runtime.py']
)