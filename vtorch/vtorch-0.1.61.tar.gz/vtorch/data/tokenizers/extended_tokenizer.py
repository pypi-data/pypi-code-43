import re
from itertools import chain
from overrides import overrides
from .tokenizer import Tokenizer
from pynlple.processing.token import EMOJI_COMPOUND_REGEX

LITERAL_DASH_EXCEPTIONS = ['из-за', 'из-под', 'гран-при', 'e-mail', 'он-лайн', 'сыр-бор', 'плей-офф',
                           'push-up', 'ей-богу', 'k-pop', 'к-поп', 'on-line']
JOINT_PREFIXES = ['из', 'р', 'кол', 'пр', 'г', 'б', 'из', 't', 'g', ' туда', 'sim', ' кока', 'coca', 'сим', 'кв']
JOINT_DIGIT_PREFIXES = ['ф', 'омега']
DIGIT_SUFFIXES = ['р']
PARTICLE_PREFIXES = ['по', 'во', 'в', 'кое', 'пол', 'не', 'стоп', 'микро', 'форс']
JOINT_SUFFIXES = ['на', 'во', 'fi', 'р', 'н', 'на', 'не', 'ну', 'он', 'т', 'ва']
PARTICLE_SUFFIXES = ['то', 'я', 'нибудь', 'и', 'х', 'й', 'как', 'го',
                     'либо', 'что', 'таки', 'м', 'у', 'вот', 'е', 'летний', 'летнего', 'летняя',
                     'летия', 'летию', 'летней', 'летию', 'летия', 'к', 'ти',  # 'р',  # -must work for only for 0-р
                     'd', 'кто', 'ой', 'ка', 'же', 'бы', 'ли', 'ю', 'ом', 'ый', 'та', 'ли',
                     'ого', 'мм', 'ая', 'нить', 'ку', 'ое', 'ап', 'другой', 'ых', 'ть']


@Tokenizer.register("extended_tokenizer")
class ExtendedTokenizer(Tokenizer):
    TOKEN_TYPES = [
        r'|'.join(LITERAL_DASH_EXCEPTIONS),
        #             r'|'.join(map('((?<=^)|(?<=[\W_])){}(?=$|[\W_])'.format, LITERAL_DASH_EXCEPTIONS)),

        r'((?<=^)|(?<=[\W_]))(' + '|'.join(JOINT_DIGIT_PREFIXES) + ')-\d+',
        r'(((?<=^)|(?<=[\W_]))(' + '|'.join(JOINT_PREFIXES) + ')-)?[^\W\d_]+(-(' + '|'.join(
            JOINT_SUFFIXES) + ')(?=$|[\W_]))?',  # tokens of letters (+join hyphened suffixes)
        r'(?<!^)-(' + '|'.join(PARTICLE_SUFFIXES) + ')(?=$|[\W_])',
        r'((?<=^)|(?<=[\W_]))(' + '|'.join(PARTICLE_PREFIXES) + ')-(?!$)',
        r'(?<=\d)-(' + '|'.join(DIGIT_SUFFIXES) + ')(?=$|[\W_])',
        r'[^\W_]+([\'][^\W\d_]+)+',  # tokens, starting with number and ' in middle ("7'fold", etc.)
        r'\d+([,:.]\d+)*\d*',  # digital sequences, also with , : . in middle
        r'\.+',
        r'_',  # underscore as being excluded by \w and previously by [^\W\d_]+
        r'\r?\n',
        EMOJI_COMPOUND_REGEX,
        r'[^\w\d\s]',  # all individual symbols that are not alphanum or whitespaces
    ]

    def __init__(self):
        self.space_pat = re.compile(r' +')
        self.token_pat = re.compile("|".join(map('({})'.format, self.TOKEN_TYPES)))
        self.PRESPLIT_PAT = re.compile(r' +')

    def __tokenize_substr(self, str_):
        for matches in self.token_pat.finditer(str_):
            span = matches.span()
            yield matches.string[span[0]:span[1]]

    @overrides
    def tokenize(self, string_):
        return list(chain.from_iterable(map(self.__tokenize_substr, self.PRESPLIT_PAT.split(string_))))
