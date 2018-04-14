############################################################################################
# Environment Setup:                                                                       #
# 1. Install latest python3 https://www.python.org/                                        #
# 2. Install dependency requests. pip install requests                                     #
#                                                                                          #
# Run the script:                                                                          #
# i.e. python script.py -l 100 -d 'acne vulgaris' 'Rosacea'                                #
# Use `python3' on Mac if you have both python2 and python3 installed                      #
# required argument -d the dx_label (diagnosis results) you want to scrap, multiple inputs #
# required argument -l the required number of images for every dx_label                    #
############################################################################################

import requests
import json

limit = 100
dx_labels = ["Rosacea", 'acne vulgaris']
meta_data_url = "https://www.dermquest.com/Services/facetData.ashx"
search_url_base = "https://www.dermquest.com/Services/imageData.ashx"

diagnoses_roots_dict = {}
diagnoses_facets = {}
lesions_facets = {}

def scrapData(limit, dx_labels):
    """
    Scarp limit number of images data for given dx_labels.
    Report the image_url, dx_label and lesion_label into file result.csv

    :param limit: the required number of images for each diagnosis result
    :param dx_labels: the diagnosis results you want to scrap
    :return:
    """
    fetchAndParseMetadata()
    print(lesions_facets)
    for dx_label in dx_labels:
        dx_label_diagnosis_id = findDiagnosisId(dx_label)
        if not dx_label_diagnosis_id:
            print("Can not find this diagnosis : ", dx_label)
            continue
        print(dx_label_diagnosis_id)
        # page = 0
        # perPage = 128
        # search_result_file_name = dx_labels
        # try:
        #     file = open(file_name + , 'r')
        # except FileNotFoundError:
        #     r = requests.get(meta_data_url)
        #     file = open(file_name, 'w')
        #     file.write(r.text)
        #     file.close()
        #     file = open(file_name, 'r')

def fetchAndParseMetadata():
    file_name = "metadata.txt"
    try:
        file = open(file_name, 'r')
    except FileNotFoundError:
        r = requests.get(meta_data_url)
        file = open(file_name, 'w')
        file.write(r.text)
        file.close()
        file = open(file_name, 'r')
    parsed_json = json.loads(file.read())
    file.close()

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

def findDiagnosisId(dx_label):
    first_char = dx_label[0].upper()
    list_diagnoses = diagnoses_roots_dict[first_char]
    for diagnosis_id in list_diagnoses:
        if diagnoses_facets[str(diagnosis_id)]['Text'].lower() == dx_label.lower():
            return diagnosis_id
    return None

scrapData(limit, dx_labels)