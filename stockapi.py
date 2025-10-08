from yahoo_fin import stock_info as si
import datetime
import re
import logging as l

log = l.getLogger("stockapi")


def get_ticker_live(ticker):
    return si.get_live_price(ticker)


def get_ticker_df(ticker, def_days=90):
    days = def_days * 7 / 5  # convert into number of trading days
    before = datetime.datetime.today() - datetime.timedelta(days=days)
    df = None
    try:
        # replace dot with dash - only occurs for BRK.B and BF.B
        ticker = re.sub(r"([a-z])\.([a-z])", r"\1-\2", ticker, 0, re.IGNORECASE)
        df = si.get_data(ticker, start_date=before)
    except Exception as e:
        log.info(f"Exception {e} getting data for {ticker}")

    return df


def get_portfoilo_alloc(df):
    # return embelishished copy of input
    tmp = df.copy()
    tmp["mkt_value"] = tmp.shares * tmp.ticker.apply(lambda x: get_ticker_live(x))
    tmp["current_alloc"] = tmp.mkt_value / tmp.mkt_value.sum()
    return tmp


ticker_to_idx = {"sp500": "SPY"}


def index_50_above_200(index="sp500"):
    ticker = ticker_to_idx[index]
    idx_df = get_ticker_df(ticker, 300)
    ma50 = idx_df.rolling(50).mean()[-1]
    ma200 = idx_df.rolling(200).mean()[-1]
    return ma50 > ma200


def get_sp500_tickers():
    return si.tickers_sp500()


def get_nasdaq_tickers():
    return si.tickers_nasdaq()


def get_dow_tickers():
    return si.tickers_dow()


idx_dict = {
    "sp500": get_sp500_tickers,
    "nasdaq": get_nasdaq_tickers,
    "dow": get_dow_tickers,
}


def index_ticker_fn(idx_name):
    log.info("index_ticker_fn: " + idx_name)
    tmp = idx_dict.get(idx_name)
    if tmp is not None:
        return tmp
