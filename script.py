###########################################################################################
# Environment Setup                                                                       #
# 1. Install latest python3 https://www.python.org/                                       #
# 2. Install dependency requests. pip install requests                                    #
# 3. Install dependency beautiful soup 4. pip install beautifulsoup4                      #
###########################################################################################

import argparse
import re
import requests
import sys
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='-l, -limit set up number of images \n -d, -dx_label the list of ')
args = parser.parse_args()

# r = requests.get('https://www.dermquest.com/results/?q=Rosacea')
# print(r.status_code)
# #200
# print(r.headers['content-type'])
# #'application/json; charset=utf8'
# print(r.encoding)

# file = open("index2.html", "r")
# soup = BeautifulSoup(file.read(), "html5lib")
# res = soup.find_all('span', class_="image-rating")

# print(len(res))
# for i in range(len(res)):
#     print(res[i])
#     print(res[i].find_next('h3', text=re.compile('Primary Lesions')).find_next('ul'))
#     print(res[i].find_next('h3', text=re.compile('Pathophysiology')).find_next('ul'))
#     # To implement, if Pathophysiology match expected dx_label, query image url and get lesion label


if __name__ == '__main__':
    print(len(sys.argv))
    for e in sys.argv:
        print(e)