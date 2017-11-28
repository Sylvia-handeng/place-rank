from __future__ import print_function
from lxml import html
import requests
from dict2xml import dict2xml as xmlify
import json
import pandas as pd
import numpy as np
import pickle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import urllib
import re
from yelp import query_api
import matplotlib.pyplot as plt
from collections import Counter

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

coorlist=[]

allRes={}
allRes['name']=[]
allRes['lat']=[]
allRes['lon']=[]
allRes['gopen_now']=[]
allRes['vicinity']=[]
allRes['types']=[]
allRes['url']=[]
allRes['pop']=[]

CLIENT_ID = 'H6j4ajh3R67T15sIpsqPXA'
CLIENT_SECRET = 'jsnjXTq7ggq0mvV621EVVvfOtixyKZbr3y9ZCyVkSuiE5Qzmv4o1B6r9Sov4bWIA'

# API constants
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'

DEFAULT_TERM = 'food'
DEFAULT_LOCATION = 'New York, NY'#'40.731509,-73.99212'
SEARCH_LIMIT = 3

def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

def getAllGPS():
	for a in frange(40.7,40.811,0.05):#frange(40.7,40.811,0.002):
		for b in frange(-74.028,-73.995,0.05):#frange(-74.028,-73.995,0.002):
			coorlist.append(str(a)+","+str(b))	
	return(coorlist)

coorlist=getAllGPS()
driver = webdriver.Chrome()

def getIndexes(url): # grab past value from mon-sun,6am-12am,18 values a day and current live value	
	res = {}
	res['time']=[]
	res['Mon']=[]
	res['Tue']=[]
	res['Wed']=[]
	res['Thu']=[]
	res['Fri']=[]
	res['Sat']=[]

	value = []
	live_tex = []
	live_value=[]

	times=[]
	valuess=[]

	driver.get(url)
	# ("section-star-display")
	# ("section-rating-term").text  # 2 elements: # of reviews, # of dollars	
	value = driver.find_elements_by_class_name("section-popular-times-bar")
	live_tex = driver.find_elements_by_class_name("section-popular-times-live-description")
	live_value = driver.find_elements_by_class_name("section-popular-times-live-value")
	if len(live_tex) != 0:
		res['live_text'] = live_tex[0].text
		# text is an object of webElemenet
	if len(live_value) != 0:
		res['live_value'] = live_value[0].get_attribute("aria-label")
	for ele in range(len(value)):
		classname = value[ele].get_attribute("class")
		if classname.find("live") == -1:
			index_list=value[ele].get_attribute("aria-label").split(" busy at ")
			if len(index_list)==2 and 'M' in index_list[1]:
				times.append(index_list[1])
				valuess.append(float(re.sub(r'%','',index_list[0])))
			if "Current" in str(value[ele].get_attribute("aria-label")):
				res['current_value'] = value[ele].get_attribute("aria-label") 

	res['time'].append(list(Counter(times).keys()))
	for i in range(len(times)):
		appeared=list(Counter(times[:i+1]).values())[list(Counter(times[:i+1]).keys()).index(times[i])]
		j=i
		if appeared==1:
			res['Mon'].append(valuess[j])
		elif appeared==2:
			res['Tue'].append(valuess[j])
		elif appeared==3:
			res['Wed'].append(valuess[j])
		elif appeared==4:
			res['Thu'].append(valuess[j])
		elif appeared==5:
			res['Fri'].append(valuess[j])
		elif appeared==6:
			res['Sat'].append(valuess[j])
	print(res)			
	return res
	

for a in range(len(coorlist)):
	page=requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+coorlist[a]+"&radius=55&keyword=restaurant&key=AIzaSyCs9iFQSqVfgFtPhey4WB-zwHd5hhJPeYs")#key1=AIzaSyA4ZJTg8gVk9Dg4O_nI3LDCeXrZwXfaU2c  key2=AIzaSyCs9iFQSqVfgFtPhey4WB-zwHd5hhJPeYs
	tree=html.fromstring(page.content)

	stuff=tree.xpath('//body/p/text()')#stuff id list()
	stuff2=xmlify(stuff)#stuff2 becomes string
	stuff3=json.loads(stuff2)#stuff3 set to be json

	if len(stuff3['results']) != 0:
		for b in range(len(stuff3['results'])):
			name=re.sub(r'&amp;', '&', stuff3['results'][b]['name'])
			allRes['name'].append(name)
			page2=requests.get("https://maps.googleapis.com/maps/api/place/details/json?key=AIzaSyCs9iFQSqVfgFtPhey4WB-zwHd5hhJPeYs&placeid="+stuff3['results'][b]['place_id'])
			tree2=html.fromstring(page2.content)
			stu=tree2.xpath('//body/p/text()')
			stu2=xmlify(stu)
			stu3=json.loads(stu2)
			allRes['url'].append(stu3['result']['url'])
			allRes['lat'].append(stuff3['results'][b]['geometry']['location']['lat'])
			allRes['lon'].append(stuff3['results'][b]['geometry']['location']['lng'])
			allRes['vicinity'].append(stuff3['results'][b]['vicinity'])
			allRes['types'].append(stuff3['results'][b]['types'])
			try:
				allRes['gopen_now'].append(stuff3['results'][b]['opening_hours']['open_now'])
			except:
				allRes['gopen_now'].append("N/A")

for ele in range(len(allRes['url'])):
	allRes['pop'].append(getIndexes(allRes['url'][ele]).copy())
	print(str(ele+1)+" Place(s) Scraped")
# getIndexes("https://maps.google.com/?cid=12777293506627589287") #for testing

# print(allRes)

try:
    for i in range(len(allRes['name'])):
    	query_api(allRes['name'][i],allRes['lat'][i],allRes['lon'][i])
    	fig, ax=plt.subplots()
    	re1=ax.bar(np.arange(18),allRes['pop'][i]['Mon'],0.1) 
    	re2=ax.bar(np.arange(18)+0.1,allRes['pop'][i]['Tue'],0.1)
    	re3=ax.bar(np.arange(18)+0.2,allRes['pop'][i]['Wed'],0.1)
    	re4=ax.bar(np.arange(18)+0.3,allRes['pop'][i]['Thu'],0.1)
    	re5=ax.bar(np.arange(18)+0.4,allRes['pop'][i]['Fri'],0.1)
    	re6=ax.bar(np.arange(18)+0.5,allRes['pop'][i]['Sat'],0.1)
    	ax.set_xticks(np.arange(18)+0.25)
    	ax.set_xticklabels(allRes['pop'][i]['time'][0])
    	ax.set_yticklabels(np.arange(0,120,20))
    	ax.set_title(allRes['name'][i])
    	ax.legend((re1[0],re2[0],re3[0],re4[0],re5[0],re6[0]),list(allRes['pop'][i].keys())[1:])
    	fig.set_size_inches(10, 5)
    	plt.show()
except HTTPError as error:
    sys.exit(
        'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
            error.code,
            error.url,
            error.read(),
        )
    )


# Res=pd.DataFrame(allRes)
# with open('res.pickle','wb') as mydata:
# 	pickle.dump(Res,mydata)
