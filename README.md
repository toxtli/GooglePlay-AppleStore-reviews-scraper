# GooglePlay-AppleStore-reviews-scraper

## How to run it

### Instructions

Install the requirements by running this command:

> pip install -r requirements.txt

You have to had Firefox and Geckodriver installed before running the script.

### For Google Play

The company ID is the is the one that starts with com.* in the Google Play URL.

> python app.py --site google --companies com.facebook.katana

### For the App Store

The company ID is the is the number after the id* in the App Store URL.

> python app.py --site apple --companies 284882215


If there is more than one company, you can separate it by commas.