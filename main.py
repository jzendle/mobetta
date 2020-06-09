import stockapi as s
import utils as u
import regression as r
import pandas as pd
import logging as l

l.basicConfig(filename='output.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=l.INFO)
log = l.getLogger('main')

def index_df_to_analysis(idx_name):

    fname = idx_name + '.p'
    df = u.read_pickle(fname)
    tickers = df.ticker.unique()

    results_df = u.new_analysis_df()
    for idx, ticker in enumerate(tickers):
        ticker_df = df.query('ticker == @ticker')
        if ticker_df is None:
            log.info('no data for ' + ticker)
            continue
        len_data = len(ticker_df)
        if len_data < 80:
            log.info('not enough data for ' + ticker + ' - only ' + str(len_data) + ' days of data')
            continue
        (ranking, ma, gap) = r.get_stats(ticker_df)
        results_df.loc[idx] = [ticker, ranking, ma, gap]

    results_df = results_df.sort_values(by=['rank'], ascending=False)

    analysis_fname = 'analysis-' + fname

    u.pickle_file(results_df, analysis_fname)
    create_portfolio(analysis_fname)

    return results_df

def index_to_df(index_name):

    log.info('retrieving data for index: '+ index_name)

    fname = index_name + '.p'
    results_df = u.new_stock_df()
    tickers = s.index_ticker_fn(index_name)()
    for ticker in tickers:
        ticker_df = s.get_ticker_df(ticker)
        if ticker_df is None:
            log.info('unable to get data for ' + ticker)
            continue
        results_df = results_df.append(ticker_df)
    u.pickle_file(results_df, fname)
    return results_df

def create_portfolio(fname):
    portfolio_name = 'port-new-' + fname 
    df = u.read_pickle(fname)
    portfolio = df.sort_values(by=['rank'], ascending=False).query('gap == False').head(30)
    u.pickle_file(portfolio, portfolio_name)

def usage():
    print('usage: python main.py [--pull | --analyze] # default is to pull and analyze ')

if '__main__' == __name__:
    import sys
    did_something = False
    indxs = [ 'nasdaq' ,'sp500', 'dow']
    if len(sys.argv) == 1 or sys.argv[1] == '--pull':
        [index_to_df(idx) for idx in indxs]
        did_something = True
    if len(sys.argv) == 1 or sys.argv[1] == '--analyze':
        [index_df_to_analysis(idx) for idx in indxs]
        did_something = True
    
    if not did_something:
        usage()




# notes
# df[df['ticker'] == 'A'] - select all rows with ticker 'A'
# df.query('ticker == "A"')
# df.query("ticker == @tr") where tr is a variable
# df.ticker.unique() all the unique ticker symbols
