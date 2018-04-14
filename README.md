# webscraping

## Environment Setup

1. Install latest [```python3```](https://www.python.org/)

2. Install dependency ```requests```. ```pip install requests```

3. Install dependency ```beautiful soup 4```for running old script. ```pip install beautifulsoup4```

## Run the script

```bash
i.e. python script.py -l 100 -d 'acne vulgaris' 'Rosacea'
```

Use ```python3``` on Mac if you have both python2 and python3 installed.

required argument -d the dx_label (diagnosis results) you want to scrap, multiple inputs.

required argument -l the required number of images for every dx_label.

## Note for scripts

1. First approach, use requests & beautiful soup 4. I will work when when search is working on website. Check [old script](script__old.py)

2. Second thought is Selenium. It will work with page navigation. But Selenium is too slow and hard to figure out navigation tabs / button clicks.

3. Finally, go with low level. Find out how those buttons work in the back end. 

```
https://www.dermquest.com/Services/facetData.ashx // fetch metadata
https://www.dermquest.com/Services/imageData.ashx?diagnosis=109491&page=1&perPage=128  //query for specific diagnosis
```
