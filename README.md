# Title: EDGAR Fund Finder
### Author: Hasan Abdullah
##### Description: Python3 code that parses fund holdings pulled from EDGAR, given a ticker or CIK, and writes a .tsv file from them.
##### Requirements: This program assumes you have python3 and pip3 installed.

##### Instructions:
1. If you haven't done so already, navigate to the directory containing this file in your command prompt.
2. Now, to install the dependencies, type: `pip3 install -r requirements.txt`
3. Next, to run the program, type: `python3 main.py`
4. Enter the ticker or CIK when prompted. Answer the following prompt(s) as well.
5. Assuming there are no errors (e.g. 404 Not Found), the report(s) will be written to a .tsv file.

##### Notes:
- Occasionally, the server will take some time to respond to the request; in these cases, the program exits after a few seconds.
- For the (Y/N) inputs, typing anything other than `y` or `yes` (case insensitive) counts as `n` or `no`.
