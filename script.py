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
import csv
from bs4 import BeautifulSoup

# Global variables. Some base url that applied for all dx_labels.
# Based on analysis DermQuest website url on 4/10/2018. 
# It is possible become invalid later on.
search_url_base = "https://www.dermquest.com/search-results-list/"
summary_url_base = "https://www.dermquest.com/image-library/image/"
image_url_bases= "https://www.dermquest.com/imagelibrary/large/"

def scrapData(limit, dx_labels):
    """ Scarp limit number of images data for given dx_labels.
        Report the image_url, dx_label and lesion_label into file result.csv
    
    Arguments:
        limit {integer} -- the required number of images for each diagnosis result
        dx_labels {list} -- the diagnosis results you want to scrap
    """
    
    first_row = [['image_url', 'dx_label', 'lesion_label']]
    with open('result.csv', 'w') as f:
        a = csv.writer(f)
        a.writerows(first_row)
        for dx_label in dx_labels:
            print("Start scraping data for " + dx_label)
            # maintain a data_image_id array to avoid duplicate image results
            # data_image_id and image_url are one to one mapping 
            data_image_ids =[]
            count = 1
            images_page = 0
            while count <= limit:
                # get and parser search page
                search_result_dict = parserSearchPage(dx_label, str(images_page))
                images_page += 1
                for data_image_id, image_url in search_result_dict.items():
                        if data_image_id in data_image_ids:
                            continue
                        data_image_ids.append(data_image_id)
                        # get and parser case overview page.
                        data = parserCaseOverviewPage(dx_label, data_image_id, image_url)
                            a.writerows(data)
                            count += 1
                        if count > limit:
                            break
    f.close()

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

def validImageUrl(image_url):
    r = requests.head(image_url)
    return r.status_code == requests.codes.ok

# Parser search result html page:
# 1. The 'ul' tag with class search-list contains list 'li' tags
# i.e.  
# <ul class="search-list">
# <li>
#     <img src="/imagelibrary/thumb/10481-DSC00191.JPG" alt="" height="49px" class="imgLeft">
#     <h3><a href="/image-library/image/5044bfd1c97267166cd67491">Case 10911</a></h3>
#     <p>
#         nodulo cystic acne vulgaris
#     </p>
#     <div style="clear:both;"></div>
# </li>
# ....
#
# For next 'li' tag's children, we can extract the data-image-id (5044bfd1c97267166cd67491) from 'a' tag.
# This is useful for case overview page parser.
# By concatnating with summary_url_base, we can form case overview url
#
# 2. Every 'li' tag has child 'img' tag which contains the image name. 
# It can be used to form the large image url.
# We can extract the image file name (10481-DSC00191.JPG)
#
# 3. We need to validate image_url. Add this image info unless it is a valid image url.
#
# 4. Usually, the 'p' tag has the diagnosis result for the image. So, we can validate it.
# It is possible that search result diagnosis doesn't match dx_label because of other 
# infos matching dx_label. We drop the image in this case.
def parserSearchPage(dx_label, images_page):

    result_dict = {}
    # Grab the search result html page with given dx_label, images_page。 write into local
    # The file name format will be "query_result_"+dx_label+".html"
    search_file_name = "query_result_" + dx_label + "_" + images_page + ".html"

    # Can comment out this line if have files locally
    getPage(search_url_base, search_file_name, {'imagesPage': images_page, 'q': dx_label})

    # Read the local search result file we created.
    search_result_file = open(search_file_name, "r")
    search_result_soup = BeautifulSoup(search_result_file.read(), "html5lib")
    search_result_file.close()
    summary_list = search_result_soup.find('ul', class_="search-list").find_all('li')
    
    for li in summary_list:
        data_image_id = li.find('a')['href'].split('/')[3]
        img_name = li.find('img')['src'].split('/')[3].split('?')[0]
        image_url = image_url_bases + img_name
        diagnosis = li.find('p').text.strip()

        # Only add into result dict if it is a valid image url and diagnosis does match dx_label
        if re.search(dx_label, diagnosis, re.IGNORECASE) and validImageUrl(image_url):
            result_dict[data_image_id] = image_url
    
    return result_dict

# Parser case overview html page:
# 1. Each case overview page can have multiple tag <div class="case-summary">
# It contains tag <span data-image-id="5044bfd1c97267166cd67486" class="image-rating">2</span>
# and list infomations for this image, i.e. Patient case no. Patient details, etc.
# For our task, diagnosis (dx_label) and Primary Lesions are the infomations we needed.
# 
# 2. We can only search the given data_image_id's case-summary. In order to reduce the get call 
# requesting same case overview page multiple times, we parser all images. 
#
# 3. The image in this case overview page could be some other diagnosis result (dx_label). i.e.
# https://www.dermquest.com/image-library/image/5044bfd1c97267166cd6703f 
# So it is needed to validate diagnosis when we gather lesions infomation.
def parserCaseOverviewPage(dx_label, data_image_id, image_url):

    # Grab the case overview html page by given data_image_id. 
    # Write into local. The file name format will be 'dx_label'_'data_image_id'.html.
    # Whitespace in dx_label will be replaced by '_' as well.
    case_overview_file_name = dx_label.replace(" ", "_") + "_"+ data_image_id + ".html"   
    case_overview_url =  summary_url_base + data_image_id

    # Can comment out this line if have files locally             
    getPage(case_overview_url, case_overview_file_name)

    # Read the local case overview file we created.
    case_overview_file = open(case_overview_file_name, "r")
    case_overview_soup = BeautifulSoup(case_overview_file.read(), "html5lib")
    case_overview_file.close()

    # Gather and format diagnosis result into a string
    case_overview_tag = case_overview_soup.find('span', attrs={"data-image-id" : data_image_id})
    diagnosis_result = case_overview_tag.find_next('th', text=re.compile('Diagnosis')).find_next('td')
    diagnosis = diagnosis_result.text.strip()

    # Check if dx_label is in given diagnoses (ignorecase). Return None if not match.
    if not re.search(dx_label, diagnosis, re.IGNORECASE):
        return None

    # Gather and format lesions results into a string
    lesions_results = case_overview_tag.find_next('h3', text=re.compile('Primary Lesions')).find_next('ul').find_all('li')
    lesions_results = [lesion.text.strip().replace(',', ', ').replace(' / ', ', ') for lesion in lesions_results]
    lesions = ', '.join(lesions_results)

    print("Case Overview URL: ", case_overview_url)
    print("Image URL: ", image_url)
    print("diagnosis: ", diagnosis)
    print("Primary Lesions: ", lesions)
    print()

    return [[image_url, dx_label, lesions]]

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