from scipy import stats
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
    #log.info("r-square: " + str(r_value ** 2))
    #log.info("slope: " + str(exp_slope))

    annualized = annualize(exp_slope)

    #log.info('annualized rate of return: ' + str(annualized))

    return annualized * (r_value**2)


def moving_average(closes):
    sz = len(closes)
    sum = 0

    for num in closes:
       sum += num

    return sum / sz


def get_stats(df):

    adj_closes = df['adjclose'].tolist()

    gap = is_gaps(df)
    ma = moving_average(adj_closes)
    ranking = get_ranking(adj_closes)

    return (ranking, ma, gap)


if __name__ == "__main__":
    import pandas as pd
    l.basicConfig(level=l.DEBUG)
    stock_prices = [1, 1.01, 1.00, 1.03, 1.00, 1.05, 1.00, 1.07, 1.08]
    log.info(get_ranking(stock_prices))
    
    cols = ['open','high','low','close','adjclose','volume','ticker']

    results_df = pd.DataFrame(columns=cols)

    results_df.ticker = ['ibm', 'ibm', 'ibm', 'ibm', 'ibm', 'ibm']
    results_df.open = [1, 2, 3, 4, 5, 7]
    results_df.close = [2, 3, 4, 5, 6, 8]

    is_gaps(results_df)
    
    results_df = pd.DataFrame(columns=cols)

    results_df.ticker = ['ibm', 'ibm', 'ibm', 'ibm', 'ibm']
    results_df.open = [1,   1, 2, 4, 5]
    results_df.close = [1.5, 3, 4, 4.1, 9]

    is_gaps(results_df)

    log.info(moving_average(results_df.close))
