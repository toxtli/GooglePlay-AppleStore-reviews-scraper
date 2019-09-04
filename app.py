from selenium import webdriver
from selenium.webdriver.common.keys import Keys

try:
	from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import csv
import sys
import json
import time
import pandas
import argparse

def getJson(url):
    response = urlopen(url)
    data = str(response.read().decode('UTF-8'))
    return json.loads(data)

def getReviews(appID, page=1):
    try:
        url = 'https://itunes.apple.com/rss/customerreviews/id=%s/page=%d/sortby=mostrecent/json' % (appID, page)        
        print(url)
        data = getJson(url).get('feed')
        if data.get('entry') == None:
            getReviews(appID, page+1)
            return
        
        for entry in data.get('entry'):
            if entry.get('im:name'):
                continue
            
            title = entry.get('title').get('label')
            #print(title)
            author = entry.get('author').get('name').get('label')            
            version = entry.get('im:version').get('label')
            rating = entry.get('im:rating').get('label')
            review = entry.get('content').get('label')	
            vote_count = entry.get('im:voteCount').get('label')
            
            csvData = [title,  author, version, rating, review, vote_count]
            writer.writerow(csvData)
        
        if page<10:            
            getReviews(appID, page+1)
    
    except Exception as e:
        print(e)
        time.sleep(1)

def extract_play(company, output):
	driver = webdriver.Firefox()
	url = "https://play.google.com/store/apps/details?id=" + company + "&showAllReviews=true"
	driver.get(url)
	selector = "h3 + div > div"
	records = []
	last_elems = 0
	elems = driver.find_elements_by_css_selector(selector)
	num_elems = len(elems)
	while num_elems > last_elems:
		print(num_elems)
		num_it = -1 * (num_elems - last_elems)
		last_elems = num_elems
		for elem in elems[num_it:]:
			record = {}
			spans = elem.find_elements_by_css_selector('span')
			try:
				comment = spans[12].text
			except:
				comment = ''
			comment_index = 12 if comment else 13
			comment_obj = spans[comment_index]
			buttons = comment_obj.find_elements_by_css_selector('div > button')
			if len(buttons) > 0:
				buttons[0].click()
				time.sleep(0.1)
				spans = elem.find_elements_by_css_selector('span')
				comment_obj = spans[comment_index + 1]
			record["author"] = spans[0].text
			record["date"] = spans[2].text
			record["review"] = comment_obj.text
			stars = elem.find_element_by_css_selector('div[aria-label][role="img"]')
			record["stars"] = stars.get_attribute("aria-label")
			records.append(record)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		df = pandas.DataFrame(records)
		if output == '':
			output = company + '.csv'
		df.to_csv(output, encoding='utf-8')
		time.sleep(1)
		elems = driver.find_elements_by_css_selector(selector)
		num_elems = len(elems)
		if num_elems == last_elems:
			buttons = driver.find_elements_by_css_selector('h3 + div + div > div[role="button"]')
			if len(buttons) > 0:
				buttons[0].click()
				time.sleep(1)
				elems = driver.find_elements_by_css_selector(selector)
				num_elems = len(elems)
	driver.close()

parser = argparse.ArgumentParser(description='This script extract reviews from apps.')
parser.add_argument('-s', '--site', default='google', help="The website from where the reviews are extracted.")
parser.add_argument('-c', '--companies', default='com.microsoft.bing', help="The companies to extract information.")
parser.add_argument('-o', '--output', default='', help="The output filename.")
#345323231
args = parser.parse_args()

site = args.site
output = args.output
companies = args.companies
outputs = args.output.split(',')
if site == 'apple':
	csvTitles = ['title',  'author', 'version', 'rating', 'review', 'vote_count']
	companies = args.companies.split(',')
	for i,company in enumerate(companies):
		if output == '':
			filename = company + '.csv'
		else:
			filename = outputs[i]
		myFile = open(output, "w")
		with myFile:
		    writer = csv.writer(myFile)
		    writer.writerow(csvTitles)    
		    getReviews(company)
		    myFile.close()
elif site == 'google':
	companies = args.companies.split(',')
	for i,company in enumerate(companies):
		if output == '':
			filename = output
		else:
			filename = outputs[i]
		extract_play(company, filename)