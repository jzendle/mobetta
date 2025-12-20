
import pandas as pd
import pickle
import openpyxl
from openpyxl import Workbook
from pandas import ExcelWriter


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


def pickle_file(df, filename):
    with open(filename, 'wb') as file:
        # noinspection PyTypeChecker
        pickle.dump(df, file)


def read_pickle(filename):
    return pickle.load(open(filename, 'rb'))


def read_excel(filename):
    return pd.read_excel(filename)

def append_worksheet_to_excel(spreadsheet_filename, sheet_name, df):
    workbook = openpyxl.load_workbook(spreadsheet_filename)
    writer: ExcelWriter[Workbook]
    with pd.ExcelWriter(spreadsheet_filename, engine='openpyxl') as writer:

        writer.book = workbook
        writer.sheets = dict((ws.title, ws) for ws in workbook.worksheets)

        ## Your dataframe to append. 
        df.to_excel(writer, sheet_name)


def dump_file(filename, to_query=None, num=1000000):
    print('query: {}'.format(to_query))
    df = read_pickle(filename)
    if to_query is not None:
        df = df.query(to_query, engine='python')
    sz = min(len(df) - 1, num)
    print(df.head(sz))


if __name__ == '__main__':
    import sys

    print(str(sys.argv))
    query = None
    if len(sys.argv) > 2:
        query = sys.argv[2]
    dump_file(sys.argv[1], query)
