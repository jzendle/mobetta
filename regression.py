from scipy import stats
import math


def annualize(percent, days_per_yr=250):
    return (1 + percent)**days_per_yr


def is_gaps(opens, closes, percent=0.15):
    sz = len(opens)
    for idx in range(sz):
        current_open = opens[idx]
        current_close = closes[idx]
        if abs(current_open - current_close) > (current_open * percent):
            print('hammer detected - current open: '
                  + str(current_open) + ' current_close: ' + str(current_close))
            return True
        if idx == 0:
            continue

        prev_close = closes[idx-1]
        prev_open = opens[idx-1]
        if abs(current_open - prev_close) > (prev_open * percent):
            print('gap detected - current open: '
                  + str(current_open) + ' previous_close: ' + str(prev_close))
            return True

    return False


def get_ranking(price_series):

    exp_prices = [math.log(price) for price in price_series]
    x = range(len(price_series))
    exp_slope, intercept, r_value, p_value, std_err = stats.linregress(
        x, exp_prices)

    print("r-square: " + str(r_value ** 2))
    print("slope: " + str(exp_slope))

    annualized = annualize(exp_slope)

    print('annualized rate of return: ' + str(annualized))

    return annualized * (r_value**2)


def moving_average(closes):
    sz = len(closes)
    sum = 0

    for num in closes:
        sum += num

    return sum / sz


def get_stats(df):
    opens = df['open'].tolist()
    closes = df['close'].tolist()
    adj_closes = df['adjclose'].tolist()

    gap = is_gaps(opens, closes)
    ma = moving_average(adj_closes)
    ranking = get_ranking(adj_closes)

    return (ranking, ma, gap)


if __name__ == "__main__":

    stock_prices = [1, 1.01, 1.00, 1.03, 1.00, 1.05, 1.00, 1.07, 1.08]
    print(get_ranking(stock_prices))

    opens = [1, 2, 3, 4, 5, 7]
    closes = [2, 3, 4, 5, 6, 8]

    is_gaps(opens, closes)

    opens = [1,   1, 2, 4, 5]
    closes = [1.5, 3, 4, 4.1, 9]

    is_gaps(opens, closes)

    print(moving_average(closes))
