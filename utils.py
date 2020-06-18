import pandas as pd
import pickle

def new_stock_df():
    cols = ['open','high','low','close','adjclose','volume','ticker']
    return pd.DataFrame(columns=cols)

def new_analysis_df(data=None):
    idx = 'ticker'  # make the index be the ticker then rename the index to be ticker
    df = pd.DataFrame(data=data)
    df.set_index(idx)
    return df.rename(index = {'index':idx})

def pickle_file(df,fname):
    pickle.dump(df, open(fname, 'wb'))

def read_pickle(fname):
    return pickle.load(open(fname,'rb'))

def dump_file(fname, query=None, num=1000000):
    print('query: {}'.format(query))
    df = read_pickle(fname)
    if query != None:
        df = df.query(query,engine='python')
    sz = min( len(df)-1, num-1)
    print(df.head(sz-1))

if __name__ == '__main__':
    import sys
    print(str(sys.argv))
    query = None
    if len(sys.argv) > 2:
        query = sys.argv[2]
    dump_file(sys.argv[1],query)
