############################################################################################
# Environment Setup:                                                                       #
# 1. Install latest python3 https://www.python.org/                                        #
# 2. Install dependency requests. pip install requests                                     #
# 3. Install dependency beautiful soup 4. pip install beautifulsoup4                       #
#                                                                                          #
# Run the script:                                                                          #
# i.e. python script.py -l 100 -d 'acne vulgaris' 'Rosacea'                                #
# Use `python3' on Mac if you have both python2 and python3 installed                      #
# required argument -d the dx_label (diagnosis results) you want to scrap, multiple inputs #
# required argument -l the required number of images for every dx_label                    #
############################################################################################

import argparse
import re
import requests
import sys
import os
from bs4 import BeautifulSoup

def scrapData(limit, dx_labels):
    """ Scarp limit number of images data for given dx_labels.
        Report the image_url, dx_label and lesion_label into file result.csv
    
    Arguments:
        limit {integer} -- the required number of images for each diagnosis result
        dx_labels {list} -- the diagnosis results you want to scrap
    """

    # Some base url that applied for all dx_labels
    search_url = "https://www.dermquest.com/results/"
    summary_url_base = "https://www.dermquest.com/image-library/image/"
    image_url_bases= "https://www.dermquest.com/imagelibrary/large/"   

    # Loop for dx_labels
    for dx_label in dx_labels:
        count = 0
        print("Start scraping data for" + dx_label)

        # Grab the search result html page and write into local
        # The file name format will be "query_result_"+dx_label+".html"
        # Could comment out this line if have files locally
        query_file_name = "query_result_" + dx_label + ".html"
        # getPage(search_url, query_file_name, {'q': dx_label})
        print("Success search results for " + dx_label)

        # Read the local file we created.
        query_result_file = open(query_file_name, "r")
        query_result_soup = BeautifulSoup(query_result_file.read(), "html5lib")
        query_result_file.close()

        # Parser html page:
        # 1. each <li> tag with class attr "image-summary" has the data-image-id info for every 
        # search result image.
        # i.e.  <li data-image-id="5044bfd1c97267166cd67491" class="image-summary  inactive "> 
        # We can extract the data-image-id and concatnate with summary_url_base to form
        # case overview url
        #
        # 2. every above <li> has <img> tag which contains the image name which can direct us to
        # the large image url 
        # i.e. <img src="/imagelibrary/thumb/10481-DSC00191.JPG?height=110" alt="nodulo cystic acne vulgaris" height="110" />
        # We can extract the file name (10481-DSC00191.JPG)
        list1 = query_result_soup.find_all('li', class_="image-summary")
        for i in range(len(list1)):
            if count < limit:
                data_image_id = list1[i]['data-image-id']
                summary_url = summary_url_base + data_image_id
                img_name = list1[i].find('img')['src'].split('/')[3].split('?')[0]
                image_url = image_url_bases + img_name
                
                print(summary_url, image_url)

                summary_file_name = dx_label.replace(" ", "_") + "_"+ data_image_id + ".html"
                # Could comment out this line if have files locally
                # getPage(summary_url, summary_file_name)
                print("Success get image summart for " + data_image_id)

                summary_file = open(summary_file_name, "r")
                summary_soup = BeautifulSoup(summary_file.read(), "html5lib")
                summary_file.close()

                list2 = summary_soup.find('span', attrs={"data-image-id" : data_image_id})
                lesions = list2.find_next('h3', text=re.compile('Primary Lesions')).find_next('ul').find_all('li')
                print("Primary Lesions:\n")
                for lesion in lesions:
                    print(lesion.text.strip())
                print()
                diagnosis_results = list2.find_next('h3', text=re.compile('Pathophysiology')).find_next('ul').find_all('li')
                print("Pathophysiology:\n")
                for diagnosis in diagnosis_results:
                    print(diagnosis.text.strip())

def getPage(url, fileName, urlParams={}):
    """ Help function to get page html text a url with given urlParams
        Write the html page into a file with given fileName
    """
    try:
        r = requests.get(url, params=urlParams)
        query_result_file = open(fileName, "w")
        query_result_file.write(r.text)
        query_result_file.close
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("""
    Environment Setup: 
    1. Install latest python3 https://www.python.org/                              
    2. Install dependency requests. `pip install requests`
    3. Install dependency beautiful soup 4. `pip install beautifulsoup4`
                                                                          
    Run the script:                                                   
    i.e. python script.py -l 100 -d 'acne vulgaris' 'Rosacea'
    Use `python3` on Mac if you have both python2 and python3 installed           
    required argument -d the dx_label (diagnosis results) you want to scrap, multiple inputs
    required argument -l the required number of images for every dx_label""")
    parser.add_argument("-d", "--dx_label", nargs='+', help="the dx_label (diagnosis results) you want to scrap", required=True)
    parser.add_argument("-l", "--limit", type=int, help="the required number of images for every dx_label", required=True)
    args = parser.parse_args()
    limit = args.limit
    dx_labels = args.dx_label
    scrapData(limit, dx_labels)