# GooglePlay-AppleStore-reviews-scraper

## How to run it remotely

Open the repository notebook by clicking the following link and then Run All.

https://colab.research.google.com/github/toxtli/GooglePlay-AppleStore-reviews-scraper/blob/master/notebook.ipynb

## How to run it locally

### Instructions

Install the requirements by running this command:

> pip install -r requirements.txt

You have to install Firefox and Geckodriver before running the script.

### For Google Play

The company ID is the is the one that starts with com.* in the Google Play URL.

For browser mode

> python app.py --site google --companies com.facebook.katana

For headless mode, limit of results, and output filename

> python app.py --site google --companies com.facebook.katana --number 200 --output facebook_200.csv --quiet

### For the App Store

The company ID is the is the number after the id* in the App Store URL.

> python app.py --site apple --companies 284882215


If there is more than one company, you can separate it by commas.
