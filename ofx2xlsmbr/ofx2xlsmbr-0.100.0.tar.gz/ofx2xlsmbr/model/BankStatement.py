from typing import List
from .CashFlow import CashFlow


class BankStatement(object):
    def __init__(self):
        self.inflows: List[CashFlow] = []
        self.outflows: List[CashFlow] = []

    def __repr__(self):
        bs = 'BankStatement:'
            
        bs += '\n\n\t = Inflows: = \n\t'
        for cs in self.inflows:
            bs += '\n' + str(cs)
        bs += '\n\n\t = Outflows: =\n\t'
        for cs in self.outflows:
            bs += '\n' + str(cs)
        return bs

    def __del__(self):
        self.inflows = None
        self.outflows = None

    def cashflows(self):
        return self.inflows + self.outflows

    def merge(self, other):
        self.inflows.append(other.inflows)
        self.outflows.append(other.outflows)
