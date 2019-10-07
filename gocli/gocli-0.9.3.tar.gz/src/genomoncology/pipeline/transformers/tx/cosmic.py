from genomoncology import kms
from cytoolz.curried import assoc, compose
from genomoncology.parse.doctypes import DocType, __CHILD__, __TYPE__
from genomoncology.pipeline.transformers import register, name_mapping


NAME_MAPPING = {
    # hgvs
    "chr": "#CHROM",
    "start": "POS",
    "ref": "REF",
    "alt": "ALT",
    "CNT__mint": "CNT",
    "tissues__mstring": "TISSUES",
    "tissue_frequency__mstring": "TISSUES_FREQ",
    "resistance_mutation__mstring": "RESISTANCE_MUTATION",
    "ID__mstring": "ID",
    "CDS__mstring": "CDS",
    "AA__mstring": "AA",
}


def dict_list_to_key_list(x, field):
    list_holder = []
    for i in range(len(x[field])):
        holder = ""
        keys = sorted(list(x[field][i].keys()))
        for key in keys:
            if holder != "":
                holder = holder + ";"
            holder = holder + key
        list_holder.append(holder)
    return list_holder


def dict_list_to_key_value_list(x, field):
    list_holder = []
    for i in range(len(x[field])):
        holder = ""
        keys = sorted(list(x[field][i].keys()))
        for key in keys:
            if holder != "":
                holder = holder + ";"
            holder = holder + key + "=" + str(round(x[field][i][key], 3))
        list_holder.append(holder)
    return list_holder


register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.COSMIC,
    transformer=compose(
        lambda x: assoc(
            x,
            "resistance_mutation__mstring",
            dict_list_to_key_list(x, "resistance_mutation__mstring"),
        ),
        lambda x: assoc(
            x, "tissues__mstring", dict_list_to_key_list(x, "tissues__mstring")
        ),
        lambda x: assoc(
            x,
            "tissue_frequency__mstring",
            dict_list_to_key_value_list(x, "tissue_frequency__mstring"),
        ),
        lambda x: assoc(x, "hgvs_g", kms.annotations.to_csra(x)),
        lambda x: assoc(x, __TYPE__, DocType.COSMIC.value),
        name_mapping(NAME_MAPPING),
    ),
)

register(
    input_type=DocType.AGGREGATE,
    output_type=DocType.COSMIC,
    transformer=compose(lambda x: assoc(x, __CHILD__, DocType.COSMIC.value)),
    is_header=True,
)
