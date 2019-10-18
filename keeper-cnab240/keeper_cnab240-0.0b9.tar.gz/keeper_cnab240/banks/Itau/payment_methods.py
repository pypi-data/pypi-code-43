from enum import Enum


class PaymentMethods(Enum):
    BOLETOS_ITAU = '30'
    BOLETOS_OUTROS_BANCOS = '31'
    CC_D = '06'
    CC_ITAU = '01'
    CHEQUE = '02'
    CONCESSIONARIAS = '13'
    DARF = '16'
    DARF_NORMAL = '16'
    DARF_SIMPLES = '18'
    DARJ = '21'
    DOC = '03'
    DOC_C = '03'
    DOC_D = '07'
    DOC_MESMO_TITULAR = '07'
    DOC_OUTRO_TITULAR = '03'
    DPVAT = '27'
    FGTS = '35'
    GARE_SP = '22'
    GNRE = '91'
    GPS = '17'
    IPTU = '19'
    IPVA = '25'
    ISS = '19'
    NF = '32'
    NOTA_FISCAL = '32'
    POUPANCA_ITAU = '05'
    TED = '41'
    TED_D = '43'
    TED_MESMO_TITULAR = '43'
    TED_OUTRO_TITULAR = '41'
    TITULOS_ITAU = '30'
    TITULOS_OUTROS_BANCOS = '31'
    TRIBUTOS_COD_BARRA = '91'
    TRIBUTOS_MUNICIPAIS = '19'

    @staticmethod
    def anf_segments():
        return ['32']

    @staticmethod
    def j_segments():
        return ['30', '31']

    @staticmethod
    def segment_a():
        return {
            k: v.value
            for (k, v) in PaymentMethods.__dict__.items()
            if hasattr(v, 'value') and v.value not in PaymentMethods.j_segments()
            and v.value not in PaymentMethods.anf_segments()
        }

    @staticmethod
    def segment_a_anf():
        return {**PaymentMethods.segment_a(), **PaymentMethods.segment_anf()}

    @staticmethod
    def segment_anf():
        return {
            k: v.value
            for (k, v) in PaymentMethods.__dict__.items()
            if hasattr(v, 'value') and v.value in PaymentMethods.anf_segments()
        }

    @staticmethod
    def segment_j():
        return {
            k: v.value
            for (k, v) in PaymentMethods.__dict__.items()
            if hasattr(v, 'value') and v.value in PaymentMethods.j_segments()
        }

    @staticmethod
    def transfer_methods():
        return ['01', '03', '06', '07', '41', '43']

    @staticmethod
    def transfer_doc_methods():
        return ['03', '07']

    @staticmethod
    def transfer_ted_methods():
        return ['41', '43']
