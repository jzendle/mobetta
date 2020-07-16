from scipy import stats
import pandas as pd
import math
import logging as l

log = l.getLogger('regression')

def annualize(percent, days_per_yr=250):
    return (1 + percent)**days_per_yr


def is_gaps(df, percent=0.20):
    ticker = df['ticker'][0]
    opens = df['open'].tolist()
    closes = df['close'].tolist()
    sz = len(opens)
    for idx in range(sz):
        current_open = opens[idx]
        current_close = closes[idx]
        if abs(current_open - current_close) > (current_open * percent):
            log.info(ticker + ': hammer detected - current open: '
                  + str(current_open) + ' current_close: ' + str(current_close))
            return True
        if idx == 0:  # prevent index out of bounds from logic below
            continue

        prev_close = closes[idx-1]
        prev_open = opens[idx-1]
        if abs(current_open - prev_close) > (prev_open * percent):
            log.info(ticker + ': gap detected - current open: '
                  + str(current_open) + ' previous_close: ' + str(prev_close))
            return True

    return False


def get_ranking(price_series):

    exp_prices = [math.log(price) for price in price_series]
    x = range(len(price_series))
    exp_slope, intercept, r_value, p_value, std_err = stats.linregress(
        x, exp_prices)
    intercept  # unused variable warning removal
    p_value
    std_err
    annualized = annualize(exp_slope)
    return annualized * (r_value**2)


def exponential_moving_average(df):
    window = len(df.adjclose)-1
    ema = df.adjclose.ewm(span=window, adjust=False).mean()
    return ema[len(ema)-1]

def simple_moving_average(df):
    closes = df['adjclose'].tolist()
    sz = len(closes)
    sum = 0

    for num in closes:
       sum += num

    return sum / sz


def get_stats(df):

    ticker = df['ticker'][0]
    adj_closes = df['adjclose'].tolist()
    closes = df['close'].tolist()
    current_close = closes[-1]
    current_adj_close = adj_closes[-1]
    sma = simple_moving_average(df)
    gap = is_gaps(df)
    above_ma = current_adj_close > sma
    ranking = get_ranking(adj_closes)
    atr = avg_true_range(df)

    return ranking, current_close, atr, above_ma, gap

def wwma(values, n):
    """
    J. Welles Wilder's EMA 
    """
    # returns a Series
    ewm_series = values.ewm(alpha=1/n, adjust=False).mean() 
    # now average the list 20 values
    return ewm_series[-1]

# https://en.wikipedia.org/wiki/Average_true_range

def avg_true_range(df, n=20):
    copy = df.copy()
    high = copy['high']
    low = copy.low
    close = copy.close
    # store intermediary results
    copy['tr0'] = abs(high -low)
    copy['tr1'] = abs(high - close.shift())
    copy['tr2'] = abs(low - close.shift())
    tr = copy[['tr0','tr1','tr2']].max(axis=1)
    return wwma(tr, n)

if __name__ == "__main__":
    import pandas as pd
    import utils as u
    l.basicConfig(level=l.DEBUG)
    results_df = u.new_stock_df()
    stock_prices = [1, 1.01, 1.00, 1.03, 1.00, 1.05, 1.00, 1.07, 1.08]
    log.info(get_ranking(stock_prices))
    
    results_df.ticker = ['ibm', 'ibm', 'ibm', 'ibm', 'ibm', 'ibm']
    results_df.open = [1, 2, 3, 4, 5, 7]
    results_df.close = [2, 3, 4, 5, 6, 8]

    is_gaps(results_df)
    
    results_df = u.new_stock_df()

    results_df.ticker = ['ibm', 'ibm', 'ibm', 'ibm', 'ibm']
    results_df.open = [1,   1, 2, 4, 5]
    results_df.close = [1.5, 3, 4, 4.1, 9]
    results_df.adjclose = results_df.close 

    is_gaps(results_df)

    log.info(simple_moving_average(results_df))
    log.info(exponential_moving_average(results_df))
