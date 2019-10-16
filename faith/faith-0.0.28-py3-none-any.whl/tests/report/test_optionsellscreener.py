from report.optionsellscreener.optionsellscreener import OptionSellScreener


report = OptionSellScreener(
    exp_date='2021-01-15',
    option_type='put',
    min_chance_of_profit=0.85,
    min_fund_efficiency=0.0075,
)


def test_get_all_equity_instrument_ids() -> None:
    ids = report._get_all_equity_instrument_ids()
    assert len(ids) > 0
    for i in ids:
        assert len(i) == 36


def test_format_data_row() -> None:
    formatted = report._format_data_row([
        'Some Symbol',
        1.23,
        2.34,
        0.45523,
        0.892323,
        2.45,
        3.45,
        4.56,
        123.89,
        0.00875,
        13456,
    ])
    assert formatted == [
        'Some Symbol',
        '$1.23',
        '$2.34',
        '45.52%',
        '89.23%',
        '$2.45',
        '$3.45',
        '$4.56',
        '$123.89',
        '0.88%',
        '13,456',
    ]


def test_gen_ascii_tbl_data() -> None:
    data = report._gen_ascii_tbl_data()
    assert len(data) > 0
    for row in data:
        assert len(row) == 11
