import regression as r
import stockapi as s
import utils as u
import pandas as pd
import logging as l
from datetime import date


l.basicConfig(filename='rebalance.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=l.INFO)
log = l.getLogger('rebalance')

def rebalance(spread_sheet_name, idx_name):
    portfolio_fname = 'portfolio-analysis-' + idx_name + '.p'
    bad_fname = 'not-portfolio-analysis-' + idx_name + '.p'

    port_df = u.read_pickle(portfolio_fname)
    bad = u.read_pickle(bad_fname)
    spread_sheet = u.read_excel(spread_sheet_name)

    # get current allocation
    current_alloc = s.get_portfoilo_alloc(spread_sheet)
    tickers = spread_sheet.ticker.to_list()

    bad_list = []
    new_port_df = pd.DataFrame()
    # kick out current port members that did not make the cut
    for ticker in tickers:
        if len(bad[bad.ticker == ticker]) == 0:  # not found
            tmp_df = port_df[port_df.ticker == ticker]
            if len(tmp_df) == 0:
                log.info('ticker not found {}'.format(ticker))
                bad_list.append({'ticker' : ticker, 'notes' : 'Not found'})
                continue
            new_port_df = new_port_df.append(tmp_df)
        else:
            bad_list.append({'ticker' : ticker, 'notes' : 'SELL'})
            log.info('ticker {} did not make the cut. dropping from portfolio'.format(ticker))

    # replace kicked out entries
    if len(bad_list):
        not_in_port = port_df[~port_df.ticker.isin(new_port_df.ticker)].dropna()
        new_members = not_in_port[:len(bad_list)].copy()
        new_members['notes'] = 'NEW BUY' 
        new_port_df = new_port_df.append(new_members)

    r.do_allocation(new_port_df, len(new_port_df))

    new_port_df = new_port_df.append(bad_list,ignore_index=True )

    sheet_name = 'portfolio-' + str(date.today())

    # add sheets to spreadsheet
    u.append_worksheet_to_excel(spread_sheet_name,sheet_name,new_port_df)
    u.append_worksheet_to_excel(spread_sheet_name,'current-alloc',current_alloc)

def main(argv):
    rebalance('current-portfolio.xlsx','sp500')

if __name__ == "__main__":
    import sys
    main(sys.argv)


