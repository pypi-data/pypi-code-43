from azureml.studio.modulehost.attributes import ItemInfo
from azureml.studio.common.types import AutoEnum


class PreprocessTextLanguage(AutoEnum):
    # for now we only support english
    English: ItemInfo(name='English', friendly_name='English') = ()


class PreprocessTextTrueFalseType(AutoEnum):
    TRUE: ItemInfo(name='True', friendly_name='True') = ()
    FALSE: ItemInfo(name='False', friendly_name='False') = ()


class PreprocessTextConstant:
    SentenceSeparator = "|||"
    TokenSeparator = " "
    PreprocessedColumnPrefix = "Preprocessed"
    LanguageModelDict = {PreprocessTextLanguage.English: "en_core_web_sm"}
    VerbContractionDict = {"&": "and",
                           "cannot|cant|can't|can’t": "can not",
                           "it['|’]s": "it is",
                           "won['|’]t": "will not",
                           "let['|’]s": "let us",
                           "I ['|’] m |I ['|’]m |I['|’]m ": "I am",
                           "you ['|’] re |you ['|’]re |you['|’]re ": "you are",
                           "(has|had|have|would|should|could|do|does|did)(n'|n’)t": r"\1 not"}


class PreprocessTextPattern:
    URLPattern = "(f|ht)(tp)(s?)(://)(.*)[.|/][^ ]+"
    EmailPattern = r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@" \
                   r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    SpecialCharsPattern = r"([!,\.#$%&<>\"'*“”+/=?^_`{|}~-]){3,}"
    DuplicateCharsPattern = r"([a-z])\1{2,}"


class POSTag:
    Num = "NUM"
    Sym = "SYM"
    Punct = "PUNCT"
    Pron = "PRON"
