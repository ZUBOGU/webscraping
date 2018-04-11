###########################################################################################
# Environment Setup:                                                                      #
# 1. Install latest python3 https://www.python.org/                                       #
# 2. Install dependency requests. pip install requests                                    #
# 3. Install dependency beautiful soup 4. pip install beautifulsoup4                      #
#                                                                                         #
# Run the script:                                                                         #
# python3 script.py -l 100 -d 'acne vulgaris' 'Rosacea'                                   #
# -d the dx_label (diagnosis results) you want to scrap, multiple inputs                  #
# -l the required number of images for every dx_label                                     #
###########################################################################################

import argparse
import re
import requests
import sys
from bs4 import BeautifulSoup

def getData(limit, dx_label):
    # Implement the auth and requests lastly

    # r = requests.get('https://www.dermquest.com/results/?q=Rosacea')
    # print(r.status_code)
    # print(r.headers['content-type'])
    # print(r.encoding)

    # expeire with sample page and finish the logic
    file = open("index2.html", "r")
    soup = BeautifulSoup(file.read(), "html5lib")
    res = soup.find_all('span', class_="image-rating")

    print(len(res))
    for i in range(len(res)):
        print(res[i])
        print(res[i].find_next('h3', text=re.compile('Primary Lesions')).find_next('ul'))
        print(res[i].find_next('h3', text=re.compile('Pathophysiology')).find_next('ul'))
        # To implement, if Pathophysiology match expected dx_label, query image url and get lesion label


if __name__ == '__main__':
    parser = argparse.ArgumentParser("""Environment Setup:                                                                    #
        1. Install latest python3 https://www.python.org/                              
        2. Install dependency requests. `pip install requests`
        3. Install dependency beautiful soup 4. `pip install beautifulsoup4`
                                                                          
        Run the script:                                                   
        python3 script.py -l 100 -d 'acne vulgaris' 'Rosacea'             
        -d the dx_label (diagnosis results) you want to scrap, multiple inputs
        -l the required number of images for every dx_label""")
    parser.add_argument("-d", "--dx_label", nargs='+', help="the dx_label (diagnosis results) you want to scrap")
    parser.add_argument("-l", "--limit", help="the required number of images for every dx_label")
    args = parser.parse_args()
    limit = args.limit
    dx_label = args.dx_label
    getData(limit, dx_label)