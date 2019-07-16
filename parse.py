##########################################################
##  parse.py | Hasan Abdullah                           ##
##  Functions needed to parse and generate a .tsv file  ##
##  from the HTML of the EDGAR search results page.     ##
##########################################################

import sys
import requests
from bs4 import BeautifulSoup

#  Input (string): ticker or CIK (e.g. 0001166559)
# Output (string): HTML text of search results page for @ticker (e.g. the HTML text of
# https://www.sec.gov/cgi-bin/browse-edgar?CIK=0001166559&owner=exclude&action=getcompany)
# If the status code is not 200, prints an error message and exits.
# If the server has not issued a response for 3 seconds, raises an exception.
def search_ticker(ticker):
    url = 'https://www.sec.gov/cgi-bin/browse-edgar'
    payload = {
        'CIK': ticker,
        'count': '40' # number of reports to display (change this as needed)
    }
    response = requests.get(url, params=payload, timeout=3)
    if response.status_code != 200:
        print('StatusError: status code ' + response.status_code)
        sys.exit(1)
    return response.text


# Input (string): HTML text of EDGAR search results page.
# Output - list of dictionaries representing the reports. For example:
# [{
#        'filing': '13F-HR',
#        'format': 'Documents',
#   'description': 'Quarterly report filed by institutional managers',
#   'filing_date': '2019-05-15',
#   'file_number': '028-10098'
#  }, {...}, ...]
# If the ticker or CIK was invalid, prints an error message and exits.
def parse_text(text):
    result = []
    soup = BeautifulSoup(text, 'lxml')
    table = soup.find('div', id='seriesDiv')
    if not table:
        print('TickerError: no matching ticker or CIK')
        sys.exit(1)

    tr_tags = table.find_all('tr')[1:] # ignore the first row (table headers)
    for tr in tr_tags:
        for br in tr.find_all('br'):
            br.replace_with(' - ') # replace <br> tags with ' - '

        td_tags = tr.find_all('td')
        report = {
            # remove leading and trailing spaces
                 'filing': td_tags[0].text.strip(),
                 'format': td_tags[1].text.strip(),
            'description': td_tags[2].text.strip(),
            'filing_date': td_tags[3].text.strip(),
            'file_number': td_tags[4].text.strip()
        }
        result.append(report)
    return result


# Input1 (string): filename (without file extension) to put the report data in.
# Input2 - list of dictionaries representing the reports (see the comments above parse_text function).
# Input3 - list of strings representing the filing types to be included in the file.
# Output (None): does not return anything, but creates a file named <@filename>.tsv in the current directory with the report data in it.
# If <@filename>.tsv already exists in the current directory, prompts the user if they want to overwrite or append to it.
# If the user does not want to overwrite or append, prints a message and returns None.
def create_file(filename, reports, filing_types):
    filename += '.tsv'
    create_new = False
    overwrite = False
    append = False
    try:
        with open(filename, 'x') as f:
            create_new = True
    except FileExistsError:
        x = str(input('The file "' + filename + '" exists in the current directory. Overwrite it? (Y/N) ')).lower()
        if x == 'y' or x == 'yes':
            overwrite = True
        else:
            x = str(input('Append to it? (Y/N) ')).lower()
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
        for report in reports:
            filing = report['filing']
            if filing.lower().startswith(tuple(filing_types)):
                fmt = report['format']
                description = report['description']
                filing_date = report['filing_date']
                file_number = report['file_number']
                data = [filing, fmt, description, filing_date, file_number]
                f.write('\t'.join(data) + '\n')
