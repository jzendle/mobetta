import regression as r
import utils as u
import pandas as pd
import logging as l
from datetime import date


l.basicConfig(filename='rebalance.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=l.INFO)
log = l.getLogger('rebalance')

def rebalance(spread_sheet_name, idx_name):
    analysis_fname = 'analysis-' + idx_name + '.p'
    bad_fname = 'not-portfolio-analysis-' + idx_name + '.p'

    analysis = u.read_pickle(analysis_fname)
    bad = u.read_pickle(bad_fname)
    df = u.read_excel(spread_sheet_name)
    tickers = df.ticker.to_list()

    bad_list = []
    port_df = pd.DataFrame()
    # kick out current port members that did not make the cut
    for ticker in tickers:
        if len(bad[bad.ticker == ticker]) == 0:  # not found
            tmp_df = analysis[analysis.ticker == ticker]
            if len(tmp_df) == 0:
                log.info('ticker not found {}'.format(ticker))
                bad_list.append({'ticker' : ticker, 'notes' : 'Not found'})
                continue

            port_df = port_df.append(tmp_df)
        else:
            bad_list.append({'ticker' : ticker, 'notes' : 'SELL'})
            log.info('ticker {} did not make the cut. dropping from portfolio'.format(ticker))

    r.do_allocation(port_df, len(port_df))

    port_df = port_df.append(bad_list,ignore_index=True )
    

    sheet_name = 'portfolio-' + str(date.today())

    # add sheet to spreadsheet
    u.append_worksheet_to_excel(spread_sheet_name,sheet_name,port_df)

def main(argv):
    rebalance('current-portfolio.xlsx','sp500')

if __name__ == "__main__":
    import sys
    main(sys.argv)


