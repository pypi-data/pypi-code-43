from enum import Enum

from .Origin import Origin


class CashFlowType(Enum):
    DEBIT = 1
    CREDIT = 2


class CashFlow(object):
    def __init__(self,
                 name: str = 'N/A',
                 flowType: CashFlowType = CashFlowType.DEBIT,
                 value: float = 0.0,
                 date: str = 'N/A',
                 cash_date: str = 'N/A',
                 origin: Origin = None):
        self.name = name
        self.flowType = flowType
        self.value = value
        self.date = date
        self.cash_date = cash_date
        self.origin = origin

    def __eq__(self, other):
        return (
                self.__class__ == other.__class__ and
                self.name.strip() == other.name.strip() and
                self.value == other.value and
                self.date == other.date and
                self.cash_date == other.cash_date and
                self.origin == other.origin
        )

    def __repr__(self):
        return 'CashFlow: \
                \n\tName: {} \
                \n\tType: {} \
                \n\tValue: {} \
                \n\tDate: {} \
                \n\tCash date: {} \
                \n\tOrigin: {}'.format(self.name,
                                       self.flowType.name,
                                       self.value,
                                       self.date,
                                       self.cash_date,
                                       self.origin)
