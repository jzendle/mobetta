from yahoo_fin import stock_info as si
import datetime
import re


def get_ticker_df(ticker, days=90):
    days = days * 7/5  # convert into number of trading days
    before = datetime.datetime.today() - datetime.timedelta(days=days)
    df = None
    try:
        # replace dot with dash - only occurs for BRK.B and BF.B
        ticker = re.sub(r"([a-z])\.([a-z])", r"\1-\2", ticker , 0, re.IGNORECASE)
        df = si.get_data(ticker, start_date=before)
    except Exception as e:
        print('Exception getting data for ' + str(ticker))
        print(e)

    return df


def get_sp500_tickers():
    return si.tickers_sp500()

def get_nasdaq_tickers():
    return si.tickers_nasdaq()

def get_dow_tickers():
    return si.tickers_dow()

dict = { 
    'sp500' : get_sp500_tickers,
    'nasdaq' : get_nasdaq_tickers,
    'dow' : get_dow_tickers
}

def index_ticker_fn(idx_name):
    print ( 'index_ticker_fn: ' + idx_name)
    return dict.get(idx_name)