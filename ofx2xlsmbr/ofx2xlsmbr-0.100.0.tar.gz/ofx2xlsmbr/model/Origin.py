from enum import Enum


class AccountType(Enum):
    BANKACCOUNT = 0
    CREDITCARD = 1


class Origin:

    def __init__(self, account=None, **kwargs):
        if account is None:
            self.account_id = kwargs.get('account_id')
            self.branch_id = kwargs.get('branch')
            self.institution_number = kwargs.get('institution')
            self.account_type = AccountType[kwargs.get('type')]
        else:
            self.account_id = account.acctid
            self.branch_id = None

            if hasattr(account, 'bankid'):
                self.institution_number = account.bankid
                self.account_type = AccountType.BANKACCOUNT
                if hasattr(account, 'branchid'):
                    self.branch_id = account.branchid
            else:
                self.institution_number = None
                self.account_type = AccountType.CREDITCARD

    def is_bank_account(self):
        return self.account_type and self.account_type == AccountType.BANKACCOUNT

    def __str__(self):
        return "Account:{} / Type: {}".format(self.account_id, self.account_type)

    def __eq__(self, other):
        return (
                self.account_id == other.account_id and
                self.institution_number == other.institution_number and
                self.account_type == other.account_type and
                self.branch_id == other.branch_id
        )
