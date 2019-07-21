##########################################################
##  parse.py | Hasan Abdullah                           ##
##  Functions needed to parse and generate a .tsv file  ##
##  from the HTML of the EDGAR search results page.     ##
##########################################################

import sys
import requests
from bs4 import BeautifulSoup

TIMEOUT = 10.0 # timeout (in seconds) for slow server responses

# Input: a requests.models.Response object (e.g. what requests.get returns)
# If the status code of @page is not 200, prints an error message and exits.
def test_page(page):
    if page.status_code != 200:
        print('StatusError: status code ' + page.status_code)
        sys.exit(1)


# Input1 (string): ticker or CIK (e.g. '0001166559')
# Input2 (number): maximum number of results to show on the page (defaults to 10)
# Output (string): HTML text of search results page for @ticker (e.g. the HTML
# text of https://www.sec.gov/cgi-bin/browse-edgar?CIK=0001166559&count=10)
# If the status code is not 200, prints an error message and exits.
# If the server has not issued a response for @TIMEOUT seconds, raises an exception.
def search_ticker(ticker, num_results=10):
    url = 'https://www.sec.gov/cgi-bin/browse-edgar'
    payload = {
        'CIK': ticker,
        'count': str(int(num_results)) # convert to int in case it's a float
    }
    results_page = requests.get(url, params=payload, timeout=TIMEOUT)
    test_page(results_page)
    return results_page.text


# Input1 (string): HTML text of EDGAR search results page.
# Input2 (number): maximum number of 13F reports to parse.
# Output - list of strings representing the reports. Each report is in the following format:
# <Name_1>\t<Title_1>\t<CUSIP_1>\t<Value_1>\t<SHRS_1>\t<SH/PRN_1>\t<Put/Call_1>\t<Investment Discretion_1>\t<Manager_1>\t<Sole_1>\t<Shared_1>\t<None_1>\n
# <Name_2>\t<Title_2>\t<CUSIP_2>\t<Value_2>\t<SHRS_2>\t<SH/PRN_2>\t<Put/Call_2>\t<Investment Discretion_2>\t<Manager_2>\t<Sole_2>\t<Shared_2>\t<None_2>\n
# ...
# If the ticker or CIK was invalid, prints an error message and exits.
# If the status code is not 200, prints an error message and exits.
# If the server has not issued a response for @TIMEOUT seconds, raises an exception.
def parse_text(text, num_reports):
    reports = []
    result_soup = BeautifulSoup(text, 'lxml')
    result_table = result_soup.find('div', id='seriesDiv')
    if not result_table:
        print('TickerError: no matching ticker or CIK')
        sys.exit(1)

    result_tr_tags = result_table.find_all('tr')[1:] # ignore the first row (table headers)
    # this for loop goes through a table like the one in
    # https://www.sec.gov/cgi-bin/browse-edgar?CIK=0001166559&count=10
    for result_tr in result_tr_tags:
        if int(num_reports) <= len(reports):
            break # exit for loop if @num_reports has been reached

        result_td_tags = result_tr.find_all('td')
        # Filings | Format | Description | Filing Date | File/Film Number
        filing = result_td_tags[0].text.strip() # remove leading and trailing spaces
        if not filing.startswith('13F'):
            continue # go to next @result_tr in for loop if report is not 13F

        detail_page_url = 'https://www.sec.gov' + result_td_tags[1].find('a')['href']
        detail_page = requests.get(detail_page_url, timeout=TIMEOUT)
        test_page(detail_page)
        detail_soup = BeautifulSoup(detail_page.text, 'lxml')
        # for some reason, there are two divs with the id 'formDiv' (bad front-end!)
        detail_table = detail_soup.find_all('div', id='formDiv')[-1]
        detail_tr_tags = detail_table.find_all('tr')[1:] # ignore table headers
        # this for loop goes through a table like the one in
        # https://www.sec.gov/Archives/edgar/data/1166559/000110465919029714/0001104659-19-029714-index.htm
        for detail_tr in detail_tr_tags:
            detail_td_tags = detail_tr.find_all('td')
            # Seq | Description | Document | Type | Size
            if detail_td_tags[3].text.strip() != 'INFORMATION TABLE':
                continue # go to next @detail_tr in for loop if document is not info table

            doc_page_url = 'https://www.sec.gov' + detail_td_tags[2].find('a')['href']
            doc_page = requests.get(doc_page_url, timeout=TIMEOUT)
            test_page(doc_page)
            doc_soup = BeautifulSoup(doc_page.text, 'lxml')
            doc_table = doc_soup.find_all('table')[-1]
            doc_tr_tags = doc_table.find_all('tr')[3:] # ignore the 3 table headers
            doc = ''
            # this for loop goes through a table like the one in
            # https://www.sec.gov/Archives/edgar/data/1166559/000110465919029714/xslForm13F_X01/a19-10004_1informationtable.xml
            for doc_tr in doc_tr_tags:
                doc_td_tags = doc_tr.find_all('td')
                # Name Of Issuer | Title Of Class | CUSIP | Value (x$1000) | SHRS or PRN AMT | SH/PRN | Put/Call | Investment Discretion | Manager | Sole | Shared | None
                doc_td_strings = [x.text.strip() for x in doc_td_tags]
                doc += ('\t'.join(doc_td_strings) + '\n')

            reports.append(doc)
            break # go to next @result_tr
        # info table document was not found in @detail_table
    return reports


# Input1 (string): filename (without file extension) to put the report data in.
# Input2 - list of strings representing the reports (see the comments above parse_text function).
# Output (None): does not return anything, but creates a file named @filename.tsv in the current directory with the report data in it.
# If @filename.tsv already exists in the current directory, prompts the user if they want to overwrite or append to it.
# If the user does not want to overwrite or append, prints a message and returns None.
def create_file(filename, reports):
    filename += '.tsv'
    create_new = False
    overwrite = False
    append = False
    try:
        with open(filename, 'x') as f:
            create_new = True
    except FileExistsError:
        x = str(input('The file "' + filename + '" exists in the current directory. Overwrite it? (Y/N) ')).strip().lower()
        if x == 'y' or x == 'yes':
            overwrite = True
        else:
            x = str(input('Append to it? (Y/N) ')).strip().lower()
            if x == 'y' or x == 'yes':
                append = True

    mode = ''
    if create_new or overwrite:
        mode = 'w'
    elif append:
        mode = 'a'
    else:
        print('The file "' + filename + '" was not changed.')
        return None

    with open(filename, mode) as f:
        if mode == 'w': # write the headings for a new (or overwritten) file
            f.write('Name Of Issuer\tTitle Of Class\tCUSIP\tValue (x$1000)\tSHRS or PRN AMT\tSH/PRN\tPut/Call\tInvestment Discretion\tManager\tSole\tShared\tNone')
        for report in reports:
            f.write('\n')
            f.write(report)
