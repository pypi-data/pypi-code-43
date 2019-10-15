from ofx2xlsmbr.model.BankStatement import BankStatement

class BankStatementAdder(object):
    def add(self, bankStatement_1, bankStatement_2, removeDuplicates = True) -> BankStatement:
        bnkStmt = BankStatement()

        bnkStmts = []
        if (isinstance(bankStatement_1, list)):
            bnkStmts.extend(bankStatement_1)
        else:
            bnkStmts.append(bankStatement_1)

        if (isinstance(bankStatement_2, list)):
            bnkStmts.extend(bankStatement_2)
        else:
            bnkStmts.append(bankStatement_2)

        if (removeDuplicates):
            for bs in bnkStmts:
                for inflow in bs.inflows:
                    if inflow not in bnkStmt.inflows:
                        bnkStmt.inflows.append(inflow)
                for outflow in bs.outflows:
                    if outflow not in bnkStmt.outflows:
                        bnkStmt.outflows.append(outflow)
        else:
            for bs in bnkStmts:
                bnkStmt.inflows.extend(bs.inflows)
                bnkStmt.outflows.extend(bs.outflows)

        return bnkStmt