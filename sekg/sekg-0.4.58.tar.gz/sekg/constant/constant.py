class CodeConstant:
    LABEL_CODE_ELEMENT = "code_element"
    QUALIFIED_NAME = "qualified_name"


class DomainConstant:
    LABEL_DOMAIN_TERM = "domain term"
    PRIMARY_PROPERTY_NAME = "term_name"


class HTMLTYPEConstance:
    HTML_TYPE_UNKNOWN = 0
    HTML_TYPE_API_DECLARATION = 1
    HTML_TYPE_API_SHORT_DESCRIPTION = 2
    HTML_TYPE_API_DETAIL_DESCRIPTION = 3
    HTML_TYPE_METHOD_RETURN_VALUE_DESCRIPTION = 4


class OperationConstance:
    LABEL_OPERATION = "operation"
    PRIMARY_PROPERTY_NAME = "operation_name"


class WikiDataConstance:
    LABEL_WIKIDATA = "wikidata"
    PRIMARY_PROPERTY_NAME = "wd_item_id"
    NAME = "wikidata_name"
    REALTION_SAME_AS = "same as"


class PropertyConstant:
    COMMENT = "comment"
    INSIDE_COMMENT = "inside_comment"
    STRING_LITERAL_EXPR = "string_literal_expr"
    DESCRIPTION = "short_description"
    ALIAS = "alias"
    LEMMA = "lemma"
