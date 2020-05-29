from yahoo_fin import stock_info as si
import datetime


def get_ticker_df(ticker, days=90):
    days = days * 7/5  # convert into number of trading days
    before = datetime.datetime.today() - datetime.timedelta(days=days)
    print(before)
    print(str(before))
    df = None
    try:
       df = si.get_data(ticker, start_date=before)
    except Exception as e:
        print('Exception getting data for ' + ticker)
        print(e)

    return df


def get_sp500_tickers():
    return si.tickers_sp500()
