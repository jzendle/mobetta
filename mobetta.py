import stockapi
import utils
import regression
import pandas as pd
import logging as l
from concurrent.futures.thread import ThreadPoolExecutor

# initialize logging
l.basicConfig(
    filename="output.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=l.INFO,
)
log = l.getLogger("main")


def index_df_to_analysis(idx_name):
    file_name = idx_name + ".p"  # ex. sp500.p
    df = utils.read_pickle(file_name)
    tickers = df.ticker.unique()
    results_list = []
    for ticker in tickers:
        ticker_df = df.query("ticker == @ticker")
        if ticker_df is None:
            log.info("no data for " + ticker)
            continue
        len_data = len(ticker_df)
        if len_data < 80:
            log.info(
                "not enough data for "
                + ticker
                + " - only "
                + str(len_data)
                + " days of data"
            )
            continue
        rank, current_close, vol, current_above_ma, gap = regression.get_stats(ticker_df)
        results_list.append(
            {
                "ticker": ticker,
                "rank": rank,
                "close": current_close,
                "volatility": vol,
                "cls_gt_ma": current_above_ma,
                "gap": gap,
            }
        )

    results_df = utils.new_analysis_df(results_list)
    results_df = results_df.sort_values(by=["rank"], ascending=False)

    analysis_filename = "analysis-" + file_name

    utils.pickle_file(results_df, analysis_filename)

    create_portfolio(analysis_filename)

    return results_df


def index_to_df_sync(index_name):
    log.info("retrieving data for index: " + index_name)
    f_name = index_name + ".p"
    fxn = stockapi.index_ticker_fn(index_name)
    tickers = []
    if fxn is not None:
        tickers = fxn()
    # tickers = ['AAPL']
    df_list = []
    for ticker in tickers:
        ticker_df = stockapi.get_ticker_df(ticker)
        if ticker_df is None:
            log.info("unable to get data for " + ticker)
            continue
        df_list.append(ticker_df)
    # concat the list in one shot
    results_df = utils.new_stock_df(df_list)
    log.info("done.")

    utils.pickle_file(results_df, f_name)
    return results_df


def index_to_df(index_name):
    log.info("retrieving data for index: " + index_name)
    file_name = index_name + ".p"
    fxn = stockapi.index_ticker_fn(index_name)
    tickers = []
    if fxn is not None:
        tickers = fxn()
    # tickers = ['AAPL']
    df_map_futures = {}
    log.info("starting concurrent requests ...")
    with ThreadPoolExecutor(max_workers=50) as executor:
        for ticker in tickers:
            future = executor.submit(stockapi.get_ticker_df, ticker)
            df_map_futures[future] = ticker

    log.info("submitted all jobs. waiting for responses ...")
    df_list = []
    for future in df_map_futures:
        ticker_df = future.result()
        if ticker_df is None:
            ticker = df_map_futures[future]
            log.info("unable to get data for " + ticker)
            continue
        df_list.append(ticker_df)
    # concat the list in one shot
    results_df = utils.new_stock_df(df_list)
    log.info("done.")

    utils.pickle_file(results_df, file_name)
    return results_df


def create_portfolio(analysis_filename):
    portfolio_name = "portfolio-" + analysis_filename
    the_rest_name = "not-portfolio-" + analysis_filename
    df = utils.read_pickle(analysis_filename)
    # keep the best 20% of the index - if a currently held stock falls out of this group - end of it!
    top_20_pct = int(len(df) / 5)
    portfolio = df.query("gap == False and cls_gt_ma == True").head(top_20_pct)
    the_rest = df[
        df.ticker.isin(portfolio.ticker) == False
    ]  # keep track of ones not in portfolio too

    num_assets = 20
    regression.do_allocation(portfolio, num_assets)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter("portfolio.xlsx") as writer:  # pylint: disable=abstract-class-instantiated
        portfolio.to_excel(writer, sheet_name="portfolio")
        the_rest.to_excel(writer, sheet_name="the rest")
    print(
        "sum of pct: {} sum of cost: {}".format(
            portfolio.pct_alloc.sum(), portfolio.cost.sum()
        )
    )
    utils.pickle_file(portfolio, portfolio_name)
    utils.pickle_file(the_rest, the_rest_name)
    # dump best part to screen
    utils.dump_file(portfolio_name, num=20)


def usage():
    print(
        "usage: python mobetta.py [--pull | --analyze] # default is to pull and analyze "
    )


if "__main__" == __name__:
    import sys

    usage()

    pull = len(sys.argv) == 1 or sys.argv[1] == "--pull"
    analyze = len(sys.argv) == 1 or sys.argv[1] == "--analyze"
    if not pull and not analyze:
        usage()
        exit(0)

    # indices = [ 'nasdaq' ,'sp500', 'dow']
    indices = ["sp500"]
    if pull:
        [index_to_df(idx) for idx in indices]
    if analyze:
        [index_df_to_analysis(idx) for idx in indices]

# notes

# df[df['ticker'] == 'A'] - select all rows with ticker 'A'
# df.query('ticker == "A"')
# df.query("ticker == @varname") where varname is a variable
# df.ticker.unique() all the unique ticker symbols
