import copy
from cytoolz.curried import curry, assoc
from cytoolz import merge, merge_with, reduceby

from genomoncology.parse import DocType, __TYPE__, __CHILD__
from .base import LazyFileSource
from .delimited import do_split, DelimitedFileSource


def dict_seq_reducer(seq, dict_key, value_keys, add_kv_dict=None):
    """
    Reduce a sequence of dicts to single dict of dicts,
    optionally adding additional k,v pairs
    """
    reduced_dict = dict()
    for element in seq:
        if len(element["REF"]) > 1400 or len(element["ALT"]) >= 1400:
            continue
        reduced_dict[element[dict_key]] = dict()
        for key in value_keys:
            reduced_dict[element[dict_key]][key] = element[key]
        if add_kv_dict:
            for k, v in add_kv_dict.items():
                reduced_dict[element[dict_key]][k] = v
    return reduced_dict


def _process_vcf_info(vcf_dict):
    for k, v in vcf_dict.items():
        if v.get("#CHROM") == "#CHROM":
            continue
        if "CDS" in v["INFO"]:
            vcf_dict[k]["CDS"] = [
                x for x in v["INFO"].split(";") if x[:3] == "CDS"
            ][0].split("=")[1]
        else:
            vcf_dict[k]["CDS"] = "None"
        if "AA" in v["INFO"]:
            vcf_dict[k]["AA"] = [
                x for x in v["INFO"].split(";") if x[:2] == "AA"
            ][0].split("=")[1]
        else:
            vcf_dict[k]["AA"] = "None"
    return vcf_dict


@curry
class AggregatedFileSource(LazyFileSource):
    def __init__(
        self,
        filename,
        aggregate_key,
        backup_key=None,
        delimiter="\t",
        include_header=True,
        **meta
    ):
        self.delimiter = delimiter
        self.aggregate_key = aggregate_key
        self.backup_key = backup_key
        self.include_header = include_header
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(self.meta, __TYPE__, DocType.AGGREGATE.value)

        super().__init__(filename)

    def __iter__(self):
        # noinspection PyUnresolvedReferences
        iterator = super(AggregatedFileSource.func, self).__iter__()

        self.columns = next(iterator).strip().split(self.delimiter)

        if self.include_header:
            yield self.create_header()

        aggregated_d = reduceby(
            self.get_key_value, self.get_aggregate_value, iterator, dict
        )

        for key, value in aggregated_d.items():
            value["key"] = key
            value["__type__"] = DocType.AGGREGATE.value
            yield value

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "columns": self.columns,
            "meta": self.meta,
            "file_path": self.name,
        }

    def get_key_value(self, x):
        column_index = self.columns.index(self.aggregate_key)
        elements = do_split(self.delimiter, x.replace("\n", ""))
        if column_index < len(elements) and elements[column_index] != "":
            key = elements[column_index]
        else:
            key = elements[self.columns.index(self.backup_key)].split(", ")[0]
        return key

    def get_aggregate_value(self, acc, x):
        hold_d = copy.deepcopy(acc)
        value_l = do_split(self.delimiter, x.replace("\n", ""))
        for i in range(len(value_l)):
            value = value_l[i] if value_l[i] != "" else "None"
            if self.columns[i] in hold_d:
                hold_d[self.columns[i]] = hold_d[self.columns[i]] + [value]
            else:
                hold_d[self.columns[i]] = [value]
        return hold_d


@curry
class AggregatedCOSMICSources(LazyFileSource):
    def __init__(self, filename, cosmic_tsv, include_header=True, **meta):
        self.cosmic_vcf = filename
        self.cosmic_tsv = cosmic_tsv
        self.include_header = include_header
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(self.meta, __TYPE__, DocType.AGGREGATE.value)

        super().__init__(filename)

    def __iter__(self):
        # noinspection PyUnresolvedReferences
        if self.include_header:
            yield self.create_header()

        cosmic_vcf_dict = dict_seq_reducer(
            seq=DelimitedFileSource(
                filename=self.cosmic_vcf,
                columns=[
                    "#CHROM",
                    "POS",
                    "ID",
                    "REF",
                    "ALT",
                    "QUAL",
                    "FILTER",
                    "INFO",
                ],
                delimiter="\t",
                skip_comment=True,
                comment_char="##",
                include_header=False,
            ),
            dict_key="ID",
            value_keys=["#CHROM", "POS", "REF", "ALT", "ID", "INFO"],
        )

        cosmic_vcf_dict = _process_vcf_info(cosmic_vcf_dict)

        cosmic_tsv_dict = reduceby(
            key=self.cosmic_key_value,
            binop=self.cosmic_aggregate_value,
            seq=DelimitedFileSource(
                filename=self.cosmic_tsv,
                columns=[
                    "Gene name",
                    "Accession Number",
                    "Gene CDS length",
                    "HGNC ID",
                    "Sample name",
                    "ID_sample",
                    "ID_tumour",
                    "Primary site",
                    "Site subtype 1",
                    "Site subtype 2",
                    "Site subtype 3",
                    "Primary histology",
                    "Histology subtype 1",
                    "Histology subtype 2",
                    "Histology subtype 3",
                    "Genome-wide screen",
                    "Mutation ID",
                    "Mutation CDS",
                    "Mutation AA",
                    "Mutation Description",
                    "Mutation zygosity",
                    "LOH",
                    "GRCh",
                    "Mutation genome position",
                    "Mutation strand",
                    "SNP",
                    "Resistance Mutation",
                    "FATHMM prediction",
                    "FATHMM score",
                    "Mutation somatic status",
                    "Pubmed_PMID",
                    "ID_STUDY",
                    "Sample Type",
                    "Tumour origin",
                    "Age",
                ],
                delimiter="\t",
                include_header=False,
            ),
            init={
                "CNT": 0,
                "TISSUES": {},
                "TISSUES_FREQ": {},
                "RESISTANCE_MUTATION": {},
            },
        )

        cosmic_tsv_dict = self.process_tissue_freqs(cosmic_tsv_dict)

        cosmic_merge = merge_with(merge, cosmic_vcf_dict, cosmic_tsv_dict)

        redu_d = reduceby(
            key=self.merge_key_value,
            binop=self.merge_aggregate_value,
            seq=(
                v
                for k, v in cosmic_merge.items()
                if "#CHROM" in v and v["#CHROM"] != "#CHROM"
            ),
            init={},
        )

        for key, value in redu_d.items():
            if value.get("#CHROM"):
                value["__type__"] = DocType.AGGREGATE.value
                yield value

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            # "columns": self.columns,
            "meta": self.meta,
            "file_path": self.name,
        }

    def cosmic_key_value(self, element):
        return element["Mutation ID"]

    def merge_key_value(self, element):
        return "-".join(
            [element["#CHROM"], element["POS"], element["REF"], element["ALT"]]
        )

    def cosmic_aggregate_value(self, acc, x):
        hold_d = copy.deepcopy(acc)
        hold_d["CNT"] += 1
        if x.get("Primary site") in hold_d["TISSUES"]:
            hold_d["TISSUES"][x.get("Primary site")] += 1
        else:
            hold_d["TISSUES"][x.get("Primary site")] = 1
        if x.get("Resistance Mutation") in hold_d["RESISTANCE_MUTATION"]:
            hold_d["RESISTANCE_MUTATION"][x.get("Resistance Mutation")] += 1
        else:
            hold_d["RESISTANCE_MUTATION"][x.get("Resistance Mutation")] = 1
        return hold_d

    def process_tissue_freqs(self, cosmic_dict):
        for ck, cv in cosmic_dict.items():
            for k, v in cv["TISSUES"].items():
                cosmic_dict[ck]["TISSUES_FREQ"][k] = float(v) / cv["CNT"]
        return cosmic_dict

    def merge_aggregate_value(self, acc, x):
        hold_d = copy.deepcopy(acc)
        for key in ["#CHROM", "POS", "REF", "ALT"]:
            if key not in hold_d:
                hold_d[key] = x[key]
        for key in [
            "ID",
            "CNT",
            "TISSUES",
            "TISSUES_FREQ",
            "RESISTANCE_MUTATION",
            "CDS",
            "AA",
        ]:
            if key not in hold_d:
                hold_d[key] = [x[key]]
            else:
                hold_d[key] = hold_d[key] + [x[key]]
        return hold_d
