import pandas as pd
import pickle
import openpyxl


def new_stock_df(data=None):
    cols = ['open', 'high', 'low', 'close', 'adjclose', 'volume', 'ticker']
    # return pd.DataFrame(data=data, columns=cols)
    df = pd.concat(data)
    df.columns=cols
    return df


def new_analysis_df(data=None):
    idx = 'ticker'  # make the index be the ticker then rename the index to be ticker
    df = pd.DataFrame(data=data)
    df.set_index(idx)
    return df.rename(index={'index': idx})


def pickle_file(df, fname):
    pickle.dump(df, open(fname, 'wb'))


def read_pickle(fname):
    return pickle.load(open(fname, 'rb'))


def read_excel(fname):
    return pd.read_excel(fname)


def append_worksheet_to_excel(spreadsheet_fname, sheet_name, df):
    book = openpyxl.load_workbook(spreadsheet_fname)
    with pd.ExcelWriter(spreadsheet_fname, engine='openpyxl') as writer:
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

        ## Your dataframe to append. 
        df.to_excel(writer, sheet_name)


def dump_file(fname, query=None, num=1000000):
    print('query: {}'.format(query))
    df = read_pickle(fname)
    if query != None:
        df = df.query(query, engine='python')
    sz = min(len(df) - 1, num)
    print(df.head(sz))


if __name__ == '__main__':
    import sys

    print(str(sys.argv))
    query = None
    if len(sys.argv) > 2:
        query = sys.argv[2]
    dump_file(sys.argv[1], query)
