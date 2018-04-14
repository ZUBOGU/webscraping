# webscraping

## Environment Setup

1. Install latest [```python3```](https://www.python.org/)

2. Install dependency ```requests```. ```pip install requests```

3. Install dependency ```beautiful soup 4```. ```pip install beautifulsoup4```

4. Install dependency ```beautiful soup 4```. ```pip install selenium```

## Run the script

```bash
i.e. python script.py -l 100 -d 'acne vulgaris' 'Rosacea'
```

Use ```python3``` on Mac if you have both python2 and python3 installed.

required argument -d the dx_label (diagnosis results) you want to scrap, multiple inputs.

required argument -l the required number of images for every dx_label.

## Note for scripts

Deprecated script_old.py.  it works when search is working on website. It is not working right now

Go with Selenium approach. It will work with page navigation.