import pandas as pd
import stockapi as sapi
import regression
import pickle

def do_analysis():

    sp500_df = pickle.load(open('sp500.p','rb'))
    tickers = sp500_df.ticker.unique()

    results_df = pd.DataFrame(columns=['symbol', 'rank', 'MA', 'gap'])

    # tickers = ['aapl', 'ibm']  # stockapi.get_sp500_tickers()
    # tickers = sapi.get_sp500_tickers()

    for idx, ticker in enumerate(tickers):
        print('getting data for ' + ticker)
        ticker_df = sp500_df.query('ticker == @ticker')
        if ticker_df is None:
            continue
        (ranking, ma, gap) = regression.get_stats(ticker_df)
        results_df.loc[idx] = [ticker, ranking, ma, gap]


    results_df = results_df.sort_values(by=['rank'], ascending=False)


    print(results_df.head(20))

    pickle.dump(results_df, open('analysis.p', 'wb'))

    return results_df


def sp500_ticker_df():

    cols = ['open','high','low','close','adjclose','volume','ticker']

    results_df = pd.DataFrame(columns=cols)
    tickers = sapi.get_sp500_tickers()
    #tickers = ['aapl', 'ibm']  # stockapi.get_sp500_tickers()
    for ticker in enumerate(tickers):
        ticker_df = sapi.get_ticker_df(ticker)
        if ticker_df is None:
            print('unable to get data for ' + ticker)
            continue
        results_df = results_df.append(ticker_df)
    pickle.dump(results_df, open('sp500.p', 'wb'))
    return results_df


if '__main__' == __name__:
    do_analysis()



# notes
# df[df['ticker'] == 'A'] - select all rows with ticker 'A'
# df.query('ticker == "A"')
# df.query("ticker == @tr") where tr is a variable
# df.ticker.unique() all the unique ticker symbols