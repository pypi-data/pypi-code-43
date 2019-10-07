from cytoolz.curried import curry
from collections import deque
from .base import FileSink
from govcf.variant_files import ensure_collection
from genomoncology.parse import DocType

import related


@related.immutable()
class DummyVariantRecord(object):
    chrom = related.StringField()
    pos = related.IntegerField()
    ref = related.StringField()
    alt = related.StringField()
    info = related.ChildField(dict, default=dict)

    CHR_FIELDS = ["chr", "c"]
    POS_FIELDS = ["pos", "s", "start", "hg19_pos", "hg37_pos", "hg38_pos"]
    REF_FIELDS = ["ref", "r"]
    ALT_FIELDS = ["alt", "a"]
    INFO_IGNORE = {"__type__", "build"}

    def __str__(self):
        return (
            "\t".join(
                [
                    self.chrom,
                    str(self.pos),
                    ".",
                    self.ref,
                    self.alt,
                    ".",
                    ".",
                    self.info_str,
                ]
            )
            + "\n"
        )

    @property
    def info_str(self):
        return ";".join(self.info_nvp())

    def info_nvp(self):
        for (name, value) in self.info.items():
            if name == "info":
                ivalues = value[0].items()
                for (iname, ivalue) in ivalues:
                    yield f"{iname}={ivalue}"

            elif name not in self.INFO_IGNORE:
                value_str = ",".join(map(str, value))
                yield f"{name}={value_str}"

    @classmethod
    def pop_first(cls, unit: dict, field_names: list):
        for field_name in field_names:
            value = unit.pop(field_name, None)
            if value is not None:
                return value

    @classmethod
    def create_from_unit(cls, unit: dict):
        unit = unit.copy()
        chrom = cls.pop_first(unit, cls.CHR_FIELDS)
        pos = cls.pop_first(unit, cls.POS_FIELDS)
        ref = cls.pop_first(unit, cls.REF_FIELDS)
        alt = cls.pop_first(unit, cls.ALT_FIELDS)

        info = {}
        for (name, value) in unit.items():
            info[name] = ensure_collection(value)

        return DummyVariantRecord(chrom, pos, ref, alt, info)


@curry
class VcfFileSink(FileSink):
    def __init__(self, filename):
        super().__init__(filename, insert_newlines=False)
        self.recent_records_seen = deque(maxlen=100)
        self.count = 0

    @classmethod
    def get_record_str(cls, unit) -> str:
        record = unit.get("__record__")
        if record is None:
            if DocType.HEADER.is_a(unit):
                record = DEFAULT_VCF_HEADER
            else:
                record = DummyVariantRecord.create_from_unit(unit)
        record = str(record)
        return record

    def convert(self, unit):
        self.count += 1
        record = self.get_record_str(unit)

        if record not in self.recent_records_seen:
            self.recent_records_seen.append(record)
            return record


DEFAULT_VCF_HEADER = """##fileformat=VCFv4.2
##contig=<ID=1,length=249250621>
##contig=<ID=2,length=243199373>
##contig=<ID=3,length=198022430>
##contig=<ID=4,length=191154276>
##contig=<ID=5,length=180915260>
##contig=<ID=6,length=171115067>
##contig=<ID=7,length=159138663>
##contig=<ID=8,length=146364022>
##contig=<ID=9,length=141213431>
##contig=<ID=10,length=135534747>
##contig=<ID=11,length=135006516>
##contig=<ID=12,length=133851895>
##contig=<ID=13,length=115169878>
##contig=<ID=14,length=107349540>
##contig=<ID=15,length=102531392>
##contig=<ID=16,length=90354753>
##contig=<ID=17,length=81195210>
##contig=<ID=18,length=78077248>
##contig=<ID=19,length=59128983>
##contig=<ID=20,length=63025520>
##contig=<ID=21,length=48129895>
##contig=<ID=22,length=51304566>
##contig=<ID=X,length=155270560>
##contig=<ID=Y,length=59373566>
##contig=<ID=MT,length=16569>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
"""
