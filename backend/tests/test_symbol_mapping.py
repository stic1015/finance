from app.services.market_data.symbol import normalize_symbol, to_futu_code


def test_normalize_us_symbol_defaults_to_us():
    parts = normalize_symbol("AAPL")
    assert parts.market == "US"
    assert parts.ticker == "AAPL"


def test_normalize_cn_and_hk_symbol_formats():
    assert to_futu_code("00700.HK") == "HK.00700"
    assert to_futu_code("600519.SH") == "SH.600519"
