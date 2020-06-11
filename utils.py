import pandas as pd
import pickle

def new_stock_df():
    cols = ['open','high','low','close','adjclose','volume','ticker']
    return pd.DataFrame(columns=cols)

def new_analysis_df():
    return pd.DataFrame(columns=['symbol', 'rank', 'current_above_ma', 'gap'])

def pickle_file(df,fname):
    pickle.dump(df, open(fname, 'wb'))

def read_pickle(fname):
    return pickle.load(open(fname,'rb'))

def dump_file(fname):
    df = read_pickle(fname)
    sz = len(df)
    print(df.head(sz-1))
