#!/usr/bin/python

from selenium import webdriver

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

if sys.version_info[0] >= 3:
    unicode = str

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

def click_element(driver, element):
	try:
		element.click()
	except:
		driver.execute_script("arguments[0].click();", element)
		#webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
	
def extract_play(company, headers, max_results=None, headless=False, phantom=False, gchrome=False, time_sleep=1):
	if gchrome:
		chrome_options = webdriver.ChromeOptions()
		if headless:	
			chrome_options.add_argument('--headless')
			chrome_options.add_argument('--no-sandbox')
			chrome_options.add_argument('--disable-dev-shm-usage')
		driver = webdriver.Chrome('chromedriver', options=chrome_options)
	elif phantom:
		driver = webdriver.PhantomJS()
		driver.set_window_size(1120, 550)
	else:
		options = webdriver.FirefoxOptions()
		if headless:
			options.add_argument('-headless')
		driver = webdriver.Firefox(firefox_options=options)
	url = "https://play.google.com/store/apps/details?id=" + company + "&showAllReviews=true"
	driver.get(url)
	selector = "h3 + div > div"
	records = []
	last_elems = 0
	saved = 0
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
			if not (spans is not None and len(spans) > comment_index):
				comment_obj = None
			else:
				comment_obj = spans[comment_index]
				try:
					comment = spans[comment_index].text
				except:
					comment = ''
				buttons = comment_obj.find_elements_by_css_selector('div > button')
				if len(buttons) > 0:
					click_element(driver, buttons[0])
					time.sleep(0.1)
					spans = elem.find_elements_by_css_selector('span')
					comment_obj = spans[comment_index + 1]
			record["author"] = spans[0].text
			record["date"] = spans[2].text
			record["review"] = comment
			try:
				stars = elem.find_element_by_css_selector('div[aria-label][role="img"]')
				record["rating"] = stars.get_attribute("aria-label")
			except:
				record["rating"] = ''
			try:
				record["vote_count"] = elem.find_element_by_css_selector('div[aria-label="Number of times this review was rated helpful"]').text
			except:
				record["vote_count"] = ''
			if comment_obj is not None:
				siblings = comment_obj.find_elements_by_xpath('../../*')
				record['reply'] = siblings[2].text if len(siblings) > 2 else ''
			else:
				record['reply'] = ''
			row = []
			for header in headers:
				row.append(record[header])
			writer.writerow([unicode(s).encode("utf-8") for s in row])
			#records.append(record)
			saved += 1
		#df = pandas.DataFrame(records)
		#df.to_csv(output, encoding='utf-8')
		if max_results is not None and saved >= max_results:
			break
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(time_sleep)
		elems = driver.find_elements_by_css_selector(selector)
		num_elems = len(elems)
		if num_elems == last_elems:
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(time_sleep)
			elems = driver.find_elements_by_css_selector(selector)
			num_elems = len(elems)
			if num_elems == last_elems:
				buttons = driver.find_elements_by_css_selector('h3 + div + div > div[role="button"]')
				if len(buttons) > 0:
					click_element(driver, buttons[0])
					time.sleep(1)
					elems = driver.find_elements_by_css_selector(selector)
					num_elems = len(elems)
	driver.close()

start_time = time.time()
parser = argparse.ArgumentParser(description='This script extract reviews from apps.')
parser.add_argument('-s', '--site', default='google', help="The website from where the reviews are extracted.")
parser.add_argument('-c', '--companies', default='com.microsoft.bing', help="The companies to extract information.")
parser.add_argument('-o', '--output', default='', help="The output filename.")
parser.add_argument('-n', '--number', default=None, type=int, help="The number of results.")
parser.add_argument('-q', '--quiet', action='store_true', help="Enables the headless mode.")
parser.add_argument('-p', '--phantom', action='store_true', help="Use PhantomJS.")
parser.add_argument('-g', '--gchrome', action='store_true', help="Use Google Chrome.")
parser.add_argument('-t', '--timeout', default=1, type=int, help="Time to sleep after scrolling down.")
#345323231
args = parser.parse_args()

site = args.site
output = args.output
companies = args.companies
time_sleep = args.timeout
outputs = args.output.split(',')
if site == 'apple':
	csvTitles = ['author', 'review', 'rating', 'vote_count', 'version', 'title',]
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
	csvTitles = ['author', 'review', 'rating', 'vote_count', 'date',  'reply']
	companies = args.companies.split(',')
	for i,company in enumerate(companies):
		if output == '':
			filename = company + '.csv'
		else:
			filename = outputs[i]			
		myFile = open(filename, "w")
		with myFile:
		    writer = csv.writer(myFile)
		    writer.writerow(csvTitles)    
		    extract_play(company, csvTitles, args.number, args.quiet, args.phantom, args.gchrome, time_sleep)
		    myFile.close()
			
print("--- %s seconds ---" % (time.time() - start_time))