import pandas as pd
import stockapi as sapi
import regression
import pickle

results_df = pd.DataFrame(columns=['symbol', 'rank', 'MA', 'gap'])

tickers = ['aapl', 'ibm']  # stockapi.get_sp500_tickers()
# tickers = sapi.get_sp500_tickers()

for idx, ticker in enumerate(tickers):
    print('getting data for ' + ticker)
    ticker_df = sapi.get_ticker_df(ticker)
    if ticker_df is None:
        continue
    (ranking, ma, gap) = regression.get_stats(ticker_df)
    results_df.loc[idx] = [ticker, ranking, ma, gap]


results_df = results_df.sort_values(by=['rank'], ascending=False)


print(results_df.head(20))

pickle.dump(results_df, open('save.p', 'wb'))
