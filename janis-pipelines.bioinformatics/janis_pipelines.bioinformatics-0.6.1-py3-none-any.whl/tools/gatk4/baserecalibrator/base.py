from abc import ABC
from typing import Dict, Any

from janis_core import get_value_for_hints_and_ordered_resource_tuple
from janis_core import (
    ToolInput,
    ToolOutput,
    Filename,
    Array,
    String,
    InputSelector,
    CaptureType,
    ToolMetadata,
)
from janis_bioinformatics.data_types import (
    BamBai,
    FastaWithDict,
    VcfIdx,
    Vcf,
    VcfTabix,
    Bed,
)
from ..gatk4toolbase import Gatk4ToolBase
from janis_unix import Tsv


CORES_TUPLE = [
    (
        CaptureType.key(),
        {
            CaptureType.CHROMOSOME: 1,
            CaptureType.EXOME: 1,
            CaptureType.THIRTYX: 1,
            CaptureType.NINETYX: 1,
            CaptureType.THREEHUNDREDX: 1,
        },
    )
]

MEM_TUPLE = [
    (
        CaptureType.key(),
        {
            CaptureType.CHROMOSOME: 16,
            CaptureType.EXOME: 16,
            CaptureType.THIRTYX: 32,
            CaptureType.NINETYX: 64,
            CaptureType.THREEHUNDREDX: 64,
        },
    )
]


class Gatk4BaseRecalibratorBase(Gatk4ToolBase, ABC):
    @classmethod
    def gatk_command(cls):
        return "BaseRecalibrator"

    def friendly_name(self):
        return "GATK4: Base Recalibrator"

    @staticmethod
    def tool():
        return "Gatk4BaseRecalibrator"

    def cpus(self, hints: Dict[str, Any]):
        val = get_value_for_hints_and_ordered_resource_tuple(hints, CORES_TUPLE)
        if val:
            return val
        return 1

    def memory(self, hints: Dict[str, Any]):
        val = get_value_for_hints_and_ordered_resource_tuple(hints, MEM_TUPLE)
        if val:
            return val
        return 16

    def inputs(self):
        return [
            *super(Gatk4BaseRecalibratorBase, self).inputs(),
            *Gatk4BaseRecalibratorBase.additional_args,
            ToolInput(
                "bam",
                BamBai(),
                position=6,
                prefix="-I",
                doc="BAM/SAM/CRAM file containing reads",
            ),
            ToolInput(
                "knownSites",
                Array(VcfTabix()),
                prefix="--known-sites",
                position=28,
                prefix_applies_to_all_elements=True,
                doc="**One or more databases of known polymorphic sites used to exclude "
                "regions around known polymorphisms from analysis.** "
                "This algorithm treats every reference mismatch as an indication of error. However, real "
                "genetic variation is expected to mismatch the reference, so it is critical that a "
                "database of known polymorphic sites is given to the tool in order to skip over those sites. "
                "This tool accepts any number of Feature-containing files (VCF, BCF, BED, etc.) for use as "
                "this database. For users wishing to exclude an interval list of known variation simply "
                "use -XL my.interval.list to skip over processing those sites. Please note however "
                "that the statistics reported by the tool will not accurately reflected those sites "
                "skipped by the -XL argument.",
            ),
            ToolInput(
                "reference",
                FastaWithDict(),
                position=5,
                prefix="-R",
                doc="Reference sequence file",
            ),
            ToolInput(
                "outputFilename",
                Filename(extension=".table"),
                position=8,
                prefix="-O",
                doc="**The output recalibration table filename to create.** "
                "After the header, data records occur one per line until the end of the file. The first "
                "several items on a line are the values of the individual covariates and will change "
                "depending on which covariates were specified at runtime. The last three items are the "
                "data- that is, number of observations for this combination of covariates, number of "
                "reference mismatches, and the raw empirical quality score calculated by phred-scaling "
                "the mismatch rate. Use '/dev/stdout' to print to standard out.",
            ),
            ToolInput(
                "intervals",
                Bed(optional=True),
                prefix="--intervals",
                doc="-L (BASE) One or more genomic intervals over which to operate",
            ),
        ]

    def outputs(self):
        return [ToolOutput("out", Tsv(), glob=InputSelector("outputFilename"))]

    def bind_metadata(self):
        from datetime import date

        return ToolMetadata(
            creator="Michael Franklin",
            maintainer="Michael Franklin",
            maintainerEmail="michael.franklin@petermac.org",
            dateCreated=date(2018, 12, 24),
            dateUpdated=date(2019, 1, 24),
            institution="Broad Institute",
            doi=None,
            citation="See https://software.broadinstitute.org/gatk/documentation/article?id=11027 for more information",
            keywords=["gatk", "gatk4", "broad", "base recalibrator"],
            documentationUrl="https://software.broadinstitute.org/gatk/documentation/tooldocs/current/org_broadinstitute_hellbender_tools_walkers_bqsr_BaseRecalibrator.php",
            documentation="""
First pass of the base quality score recalibration. Generates a recalibration table based on various covariates. 
The default covariates are read group, reported quality score, machine cycle, and nucleotide context.

This walker generates tables based on specified covariates. It does a by-locus traversal operating only at sites 
that are in the known sites VCF. ExAc, gnomAD, or dbSNP resources can be used as known sites of variation. 
We assume that all reference mismatches we see are therefore errors and indicative of poor base quality. 
Since there is a large amount of data one can then calculate an empirical probability of error given the 
particular covariates seen at this site, where p(error) = num mismatches / num observations. The output file is a 
table (of the several covariate values, num observations, num mismatches, empirical quality score).  
""".strip(),
        )

    additional_args = [
        ToolInput(
            "tmpDir",
            String(optional=True),
            prefix="--tmp-dir",
            default="/tmp/",
            doc="Temp directory to use.",
        )
    ]


if __name__ == "__main__":
    print(Gatk4BaseRecalibratorBase().help())
