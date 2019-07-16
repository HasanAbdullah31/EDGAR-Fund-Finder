#!/usr/bin/python3

##################################################
##  main.py | Hasan Abdullah                    ##
##  Main file invoking functions from parse.py  ##
##################################################

import re
from parse import *

def main():
    ticker = str(input('Enter ticker or CIK: '))
    if re.search('[^0-9]', ticker):
        print('TickerError: ticker or CIK must contain digits only')
        sys.exit(1)

    text = search_ticker(ticker)
    reports = parse_text(text)
    filing_types = [str(input('Enter the filing type (e.g. 13F) you want included: ')).lower()]
    while True:
        x = str(input('Enter another filing type if desired (just hit enter if you want to skip): ')).lower()
        if x: filing_types.append(x)
        else: break

    filename = str(input('Enter the filename (without file extension) to put the data in: '))
    create_file(filename, reports, filing_types)


if __name__ == '__main__':
    main()
