import xml.etree.cElementTree as etree

from cytoolz.curried import curry, assoc

from genomoncology.parse import DocType, __TYPE__, __CHILD__
from ..base import LazyFileSource


@curry
class UniprotFileSource(LazyFileSource):
    def __init__(self, filename, **meta):
        self.filename = filename
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(
                self.meta, __TYPE__, DocType.UNIPROT_RECORD.value
            )

    def __iter__(self):  # pragma: no mccabe
        yield self.create_header()

        context = etree.iterparse(self.filename, events=["start", "end"])
        # accession
        accessions = []
        # protein name
        in_protein_rec_name = False
        protein = None
        # gene name
        in_gene_name = False
        gene = None
        # domain
        in_domain = False
        domains = []
        domain_starts = []
        domain_ends = []
        # protein length
        protein_length = None
        # np_ids
        np_ids = []
        for event, elem in context:
            # accession
            if event == "start" and elem.tag == "accession":
                accessions.append(elem.text)
                continue
            # protein name
            if event == "start" and elem.tag == "recommendedName":
                in_protein_rec_name = True
                continue
            if (
                in_protein_rec_name
                and event == "end"
                and elem.tag == "fullName"
            ):
                protein = elem.text
                in_protein_rec_name = False
                continue
            # gene name
            if event == "start" and elem.tag == "gene":
                in_gene_name = True
                continue
            if (
                in_gene_name
                and event == "end"
                and elem.tag == "name"
                and "type" in elem.attrib
                and elem.attrib["type"] == "primary"
            ):
                gene = elem.text
                in_gene_name = False
                continue
            # domains
            if (
                event == "start"
                and elem.tag == "feature"
                and "type" in elem.attrib
                and elem.attrib["type"] == "domain"
            ):
                domains.append(elem.attrib["description"])
                in_domain = True
                continue
            if in_domain and event == "start" and elem.tag == "begin":
                domain_starts.append(elem.attrib["position"])
                continue
            if in_domain and event == "start" and elem.tag == "end":
                domain_ends.append(elem.attrib["position"])
                continue
            if (
                event == "end"
                and elem.tag == "feature"
                and "type" in elem.attrib
                and elem.attrib["type"] == "domain"
            ):
                in_domain = False
                continue
            # protein length
            if (
                event == "start"
                and elem.tag == "sequence"
                and "length" in elem.attrib
            ):
                protein_length = elem.attrib["length"]
                continue
            # np_ids
            if (
                event == "start"
                and elem.tag == "dbReference"
                and elem.attrib["type"] == "RefSeq"
            ):
                np_ids.append(elem.attrib["id"])
                continue
            # end of entry record
            if event == "end" and elem.tag == "entry":
                return_d = {
                    "accessions": accessions,
                    "gene": gene,
                    "protein_full_name": protein,
                    "domains": domains,
                    "domain_starts": domain_starts,
                    "domain_ends": domain_ends,
                    "protein_length": protein_length,
                    "np_ids": np_ids,
                    "__type__": DocType.UNIPROT_RECORD,
                }
                accessions = []
                gene = None
                protein = None
                domains = []
                domain_starts = []
                domain_ends = []
                protein_length = None
                np_ids = []
                elem.clear()
                yield return_d

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "meta": self.meta,
            "fields": [
                "gene",
                "protein_full_name",
                "accessions",
                "domains",
                "domain_starts",
                "domain_ends",
                "protein_length",
                "np_ids",
            ],
        }
