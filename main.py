#!/usr/bin/python3

##################################################
##  main.py | Hasan Abdullah                    ##
##  Main file invoking functions from parse.py  ##
##################################################

import re
from parse import *

def main():
    ticker = str(input('Enter ticker or CIK: ')).strip()
    if re.search('[^0-9]', ticker):
        print('TickerError: ticker or CIK must contain digits only')
        sys.exit(1)

    results_page = search_ticker(ticker)
    reports = parse_text(results_page, 1)
    filename = str(input('Enter the filename (without file extension) to put the data in: ')).strip()
    create_file(filename, reports)


if __name__ == '__main__':
    main()
