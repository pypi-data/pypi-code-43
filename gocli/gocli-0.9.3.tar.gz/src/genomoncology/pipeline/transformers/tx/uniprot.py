from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping

NAME_MAPPING = {
    "gene": "gene",
    "protein_full_name__string": "protein_full_name",
    "accessions__mstring": "accessions",
    "domains__mstring": "domains",
    "domain_starts__mstring": "domain_starts",
    "domain_ends__mstring": "domain_ends",
    "protein_length__string": "protein_length",
    "np_id__mstring": "np_ids",
}

register(
    input_type=DocType.UNIPROT_RECORD,
    output_type=DocType.UNIPROT,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.UNIPROT.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.UNIPROT_RECORD,
    output_type=DocType.UNIPROT,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.UNIPROT.value),
    ),
    is_header=True,
)
