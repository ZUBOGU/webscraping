############################################################################################
# Environment Setup:                                                                       
# 1. Install latest python3 https://www.python.org/                                        
# 2. Install dependency requests. pip install requests                                     
#                                                                                          
# Run the script:                                                                          
# i.e. python script.py -l 100 -d 'acne vulgaris' 'Rosacea' -f result.csv                  
# Use `python3' on Mac if you have both python2 and python3 installed                      
# required argument -d the dx_label (diagnosis results) you want to scrap, multiple inputs 
# required argument -l the required number of images for every dx_label
# required argument -f the csv file name you want to write into             
############################################################################################

import csv
import requests
import json
import argparse
import sys

# Description of this scarping script logic
# metadata_url and search_url_base are the key part When I finished this task
# The dermquest website diagnosis searching is not working with url manipulation
# (https://www.dermquest.com/image-library/image-search)
# On the UI, we need to manually click and selected diagnosis.Then, click view images to see results.
# So, I went with low level approach. Clicking view images actually fetches JSON data by using
# metadata_url and search_url_base with url params. Then, transfer those information into website.
# I fetched those JSON responses, parsed those data and returned row data I wanted.
# Get metadata_url will have all lesions and diagnosis data (their id and text mapping)
# The search_url_base are valid url to fetch search data. It takes url params(diagnosis id, page number
# and number of image perPage). We can loop all results for given diagnosis id. 
# It returns result with lesion ids, image file name.
# i.e. (https://www.dermquest.com/Services/imageData.ashx?diagnosis=109493&page=1&perPage=128)

metadata_url = "https://www.dermquest.com/Services/facetData.ashx"
search_url_base = "https://www.dermquest.com/Services/imageData.ashx"
image_url_bases= "https://www.dermquest.com/imagelibrary/large/"

# Global variables, store meta data infomations
diagnoses_roots_dict = {}
diagnoses_facets = {}
lesions_facets = {}

def scrapData(limit, dx_labels, csv_file_name):
    """
    Scarp limit number of images data for given dx_labels.
    Report the image_url, dx_label and lesion_label into csv_file_name

    :param limit: the required number of images for each diagnosis result
    :param dx_labels: the diagnosis results you want to scrap
    :param csv_file_name: the csv file name you want to write into
    :return:
    """
    first_row = ['image_url', 'dx_label', 'lesion_label']
    with open(csv_file_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(first_row)
        fetchAndParseMetadata()
        for dx_label in dx_labels:
            rows_data = fetchAndParseRowsData(dx_label, limit)
            for row in rows_data:
                writer.writerow(row)
    csv_file.close()

def fetchAndParseMetadata():
    """
    Help Function to fetch Metadata and update global variables
    diagnoses_roots_dict, diagnoses_facets, lesions_facets with desired data

    :return:
    """
    data = getPageData(metadata_url)
    parsed_json = json.loads(data)

    # Parse diagnoses facets, a dict with diagnosis id mapping to diagnosis text
    # In order to easier search diagnoses id, update diagnoses_roots_dict
    # It maps first char to all possible ids start with this char. i.e. "A"
    diagnoses_roots = parsed_json['facet_collection']['diagnosis']['Roots']
    diagnoses_facets.update(parsed_json['facet_collection']['diagnosis']['Facets'])
    for root in diagnoses_roots:
        diagnoses_roots_dict[diagnoses_facets[str(root)]['Text']] = diagnoses_facets[str(root)]['Facets']

    # Parse lesions facets, a dict with lesion id mapping to lesion text
    # 1. Some lesion ids are subtype of root lesions. i.e "Alopecia / scarring"
    # Its lession id is "108073" with text "scarring". Directly using this text will missing root lession
    # So I will manipulate lesions_facets dict to add root lesions in Text for those sub lesions.
    # Format will be "'root lession text' / 'sub lession text'"
    # 2. By looking at the metadata, I am only seeing 2 level depth. So, I am not considering sub lesions have
    # subtype for now.
    lesions_roots = parsed_json['facet_collection']['lesions']['Roots']
    lesions_facets.update(parsed_json['facet_collection']['lesions']['Facets'])
    for root_id in lesions_roots:
        facets = lesions_facets[str(root_id)]['Facets']
        if facets:
            text = lesions_facets[str(root_id)]['Text']
            for lesion_id in facets:
                sub_text = lesions_facets[str(lesion_id)]['Text']
                lesions_facets[str(lesion_id)]['Text'] = text + " / " + sub_text

def fetchAndParseRowsData(dx_label, limit):
    """
    Function to loop search url, parse the data and return the rows data with
    valid image url, diagnosis label and all lesions labels.
    If cannot find images with required limit number. Report as many as possible.
    Print warning message


    :param dx_label: given diagnosis label
    :param limit: the required number of images for given dx_label
    :return: The valid rows data that could write into csv file. [] if not found.
    """
    dx_label_diagnosis_id = findDiagnosisId(dx_label)
    # return empty array if dx_label not exist
    if not dx_label_diagnosis_id:
        print("Can not find this diagnosis : ", dx_label)
        return []
    
    page = 1
    count = 1
    number_of_pages = 1
    total_images = 0
    rows = []
    while count <= limit:
        # Stop the while loop when we search all pages or have enough images
        if page > number_of_pages or count > limit:
            break

        # Get search results JSON data with given page id
        data = getPageData(search_url_base, {'diagnosis': dx_label_diagnosis_id, 'page': page, 'perPage': 128})
        parsed_json = json.loads(data)
        total_images = parsed_json['Hits']
        number_of_pages = parsed_json['NumberOfPages']
        results= parsed_json['Results']
        page += 1

        # Loop the result and parse the data
        for result in results:      
            if count > limit:
                break            
            lesions = result['lesions']
            # Drop this result if no lesions
            if not lesions:
                continue

            # Use global variable lesions_facets to transfer lesion Ids to text string
            lesions_list = []
            for lesion in lesions:
                lesion_id = lesion['Id']
                lesion_text = lesions_facets[str(lesion_id)]['Text']
                lesions_list.append(lesion_text)
            lesions_string = ", ".join(lesions_list)
            image_name = result['FileName']
            image_url = image_url_bases + image_name

            # Only add this row if the image_url is valid
            if validateImageUrl(image_url):
                rows.append([image_url, dx_label, lesions_string])
                count += 1

    # Provide warning message if total_images not matched required limit
    if (total_images < limit):
        print("Warning: total images number of diagnosis {0} is {1}, less than the required number {2}.".format(dx_label, total_images, limit))
        print("Please pick another diagnosis label and csv file name to meet your requirement")
    return rows

def getPageData(url, urlParams={}):
    """
    Help Function

    :param url: the url for get request call
    :param urlParams: Optional Param. url param to compose url
    :return: text data for given page
    """
    try:
        r = requests.get(url, params=urlParams)
        return r.text
    except requests.exceptions.RequestException as e:
        print(e)
        print("Please fix connection issue and try again")
        sys.exit(1)

def validateImageUrl(image_url):
    """
    Help Function

    :param image_url: the image url to validate
    :return: True if valid image url. Otherwise, false
    """
    try:
        r = requests.head(image_url)
        return r.status_code == requests.codes.ok
    except requests.exceptions.RequestException as e:
        print(e)
        print("Please fix connection issue and try again")
        sys.exit(1)

def findDiagnosisId(dx_label):
    """
    Help method. Use global variables diagnoses_roots_dict and diagnoses_facets
    to find the diagnosis id for given diagnosis label.

    :param dx_label: diagnosis label
    :return: diagnosis_id. None if not found
    """
    first_char = dx_label[0].upper()
    list_diagnoses = diagnoses_roots_dict[first_char]
    for diagnosis_id in list_diagnoses:
        if diagnoses_facets[str(diagnosis_id)]['Text'].lower() == dx_label.lower():
            return diagnosis_id
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser("""
    Environment Setup: 
    1. Install latest python3 https://www.python.org/                              
    2. Install dependency requests. `pip install requests`
                                                                          
    Run the script:                                                   
    i.e. python script.py -l 100 -d 'acne vulgaris' 'Rosacea'
    Use `python3` on Mac if you have both python2 and python3 installed           
    required argument -d the dx_label (diagnosis results) you want to scrap, multiple inputs
    required argument -l the required number of images for every dx_label
    required argument -f the csv file name you want to write into
    """)
    parser.add_argument("-d", "--dx_label", nargs='+', help="the dx_label (diagnosis results) you want to scrap", required=True)
    parser.add_argument("-l", "--limit", type=int, help="the required number of images for every dx_label", required=True)
    parser.add_argument("-f", "--file_name", help="the csv file name you want to write into ", required=True)
    args = parser.parse_args()
    limit = args.limit
    dx_labels = args.dx_label
    csv_file_name = args.file_name
    scrapData(limit, dx_labels, csv_file_name)