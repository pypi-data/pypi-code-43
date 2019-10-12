from report.accountsummary.accountsummary import AccountSummary


def test_gen_reports(account_summary_report: AccountSummary) -> None:
    text = account_summary_report._gen_reports()
    for s in {
        'Stock Value',
        'Option Value',
        'Margin Used',
        'Account Value',
        '# of Symbols',
        'Profit on Stocks',
        'Profit on Options',
        'Profit on Call Writes',
        'Profit on Put Writes',
        'Symbol',
        '# of Shares',
        'Settled Profit',
        'Last Price',
        'Buying Power',
    }:
        assert s in text
