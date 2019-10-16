from alphavantage.alphavantageclient import avc


def test_get_price_history() -> None:
    price_history = avc.get_price_history(
        symbol='ADBE',
        time_window='daily',
        output_size='compact',
    )
    assert price_history.metadata.information == 'Daily Time Series with Splits and Dividend Events'
    assert len(price_history.time_series) > 0
