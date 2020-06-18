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
    results_list = []
    for idx, ticker in enumerate(tickers):
        ticker_df = df.query('ticker == @ticker')
        if ticker_df is None:
            log.info('no data for ' + ticker)
            continue
        len_data = len(ticker_df)
        if len_data < 80:
            log.info('not enough data for ' + ticker + ' - only ' + str(len_data) + ' days of data')
            continue
        rank, current_close, atr, current_above_ma, gap = r.get_stats(ticker_df)
        results_list.append({'ticker' : ticker, 'rank' : rank, 'close': current_close , 'avg_true_range' : atr, 'current_above_ma': current_above_ma, 'gap': gap})

    results_df = u.new_analysis_df(results_list)
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

def create_portfolio(analysis_fname):
    portfolio_name = 'port-new-' + analysis_fname 
    df = u.read_pickle(analysis_fname)
    # keep the best 20% of the index - if a currently held stock falls out of this group - end of it!
    top_20_pct = int(len(df) / 5)
    portfolio = df.sort_values(by=['rank'], ascending=False).query('gap == False and current_above_ma == True').head(top_20_pct) 
    # calculate allocation based on a $1000 total size and risk factor of 0.1% (.001)
    # num_shares = (1000 * .001) / atr == 1/ atr
    portfolio['num_shares'] = 1 / portfolio['avg_true_range'] 
    portfolio['cost'] = portfolio['num_shares'] * portfolio['close']
    # perform allocation for only the first 20 entries - our portfolio
    num_assets = 20
    portfolio['pct_alloc'] = 100 * portfolio['cost'][:num_assets] / portfolio['cost'][:num_assets].sum()
    portfolio.to_excel('portfolio.xlsx', sheet_name = 'portfolio')
    u.pickle_file(portfolio, portfolio_name)
    u.dump_file(portfolio_name,num=20)

def usage():
    print('usage: python main.py [--pull | --analyze] # default is to pull and analyze ')

if '__main__' == __name__:
    import sys

    pull = len(sys.argv) == 1 or sys.argv[1] == '--pull'
    analyze = len(sys.argv) == 1 or sys.argv[1] == '--analyze'
    if not pull and not analyze:
        usage()
        exit(0)

    #indxs = [ 'nasdaq' ,'sp500', 'dow']
    indxs = [ 'sp500']
    if pull:
        [index_to_df(idx) for idx in indxs]
    if analyze:
        [index_df_to_analysis(idx) for idx in indxs]

# notes
# df[df['ticker'] == 'A'] - select all rows with ticker 'A'
# df.query('ticker == "A"')
# df.query("ticker == @tr") where tr is a variable
# df.ticker.unique() all the unique ticker symbols
