import pandas as pd
import pickle

def new_stock_df():
    cols = ['open','high','low','close','adjclose','volume','ticker']
    return pd.DataFrame(columns=cols)

def new_analysis_df():
    return pd.DataFrame(columns=['symbol', 'rank', 'MA', 'gap'])

def pickle_file(df,fname):
    pickle.dump(df, open(fname, 'wb'))

def read_pickle(fname):
    return pickle.load(open(fname,'rb'))