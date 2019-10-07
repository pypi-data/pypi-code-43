from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    "gene": "gene",
    # info
    "phenotype__mstring": "phenotype",
    "hpo__mstring": "hpo_id",
}

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.HPO,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __TYPE__, DocType.HPO.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.HPO,
    transformer=compose(
        lambda x: assoc(x, "is_gene_annotation", True),
        lambda x: assoc(x, __CHILD__, DocType.HPO.value),
    ),
    is_header=True,
)
