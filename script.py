############################################################################################
# Environment Setup:                                                                       #
# 1. Install latest python3 https://www.python.org/                                        #
# 2. Install dependency requests. pip install requests                                     #
# 3. Install dependency beautiful soup 4. pip install beautifulsoup4                       #
#                                                                                          #
# Run the script:                                                                          #
# i.e. python3 script.py -l 100 -d 'acne vulgaris' 'Rosacea'                               #
# required argument -d the dx_label (diagnosis results) you want to scrap, multiple inputs #
# required argument -l the required number of images for every dx_label                    #
############################################################################################

import argparse
import re
import requests
import sys
from bs4 import BeautifulSoup

def scrapData(limit, dx_labels):
    search_url = "https://www.dermquest.com/results/"
    summary_url_base = "https://www.dermquest.com/image-library/image/"
    image_url_bases= "https://www.dermquest.com/imagelibrary/large/"   

    for dx_label in dx_labels:
        print("Start scraping data for" + dx_label)

        # Grab the search result html page and write into local
        # Could comment out this part code if debug locally.
        #     r = requests.get(search_url, params={'q': dx_label})
        #     query_result_file = open("query_result_"+dx_label+".html", "w")
        #     query_result_file.write(r.text)
        #     print("Success querying for" + dx_label)
        # except requests.exceptions.RequestException as e:
        #     print(e)
        #     sys.exit(1)

        # Read the local file we created.
        query_result_file = open("query_result_"+dx_label+".html", "r")
        query_result_soup = BeautifulSoup(query_result_file.read(), "html5lib")
        res = query_result_soup.find_all('span', class_="image-rating")
        for i in range(len(res)):
            print(res[i])

        # r = requests.get(search_url)
        # print(r.status_code)
        # print(r.headers['content-type'])
        # print(r.encoding)

        # expeire with sample page and finish the logic
        # file = open("index2.html", "r")
        # soup = BeautifulSoup(file.read(), "html5lib")
        # res = soup.find_all('span', class_="image-rating")

        # print(len(res))
        # for i in range(len(res)):
        #     print(res[i])
        #     print(res[i].find_next('h3', text=re.compile('Primary Lesions')).find_next('ul'))
        #     print(res[i].find_next('h3', text=re.compile('Pathophysiology')).find_next('ul'))
            # To implement, if Pathophysiology match expected dx_label, query image url and get lesion label

if __name__ == '__main__':
    parser = argparse.ArgumentParser("""
    Environment Setup: 
    1. Install latest python3 https://www.python.org/                              
    2. Install dependency requests. `pip install requests`
    3. Install dependency beautiful soup 4. `pip install beautifulsoup4`
                                                                          
    Run the script:                                                   
    i.e. python3 script.py -l 100 -d 'acne vulgaris' 'Rosacea'             
    required argument -d the dx_label (diagnosis results) you want to scrap, multiple inputs
    required argument -l the required number of images for every dx_label""")
    parser.add_argument("-d", "--dx_label", nargs='+', help="the dx_label (diagnosis results) you want to scrap", required=True)
    parser.add_argument("-l", "--limit", help="the required number of images for every dx_label", required=True)
    args = parser.parse_args()
    limit = args.limit
    dx_labels = args.dx_label
    scrapData(limit, dx_labels)