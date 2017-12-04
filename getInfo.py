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
import calendar

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
allRes['vicinity']=[]
allRes['types']=[]
allRes['url']=[]
allRes['open_days']=[]

allRes['pop_numbers']=[]
allRes['pop_info']=[]

allRes['g_open_now']=[]
allRes['g_rating']=[]
# allRes['g_#reviews']=[]
allRes['y_open_now']=[]
allRes['y_rating']=[]
allRes['y_#reviews']=[]

co=['#FF3368','#FF8D33','#FFC433','#A5FF33','#33CEFF','#3364FF','#A233FF']

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

def getIndexes(url,open_days): # grab past value from mon-sun,6am-11pm,18 values a day and current live value	
	numbers = {}
	info={}
	numbers['time']=[]
	for i in range(len(open_days)):
		if open_days[i]==0:
			numbers['Sun']=[]
		else:
			numbers[str(calendar.day_abbr[int(open_days[i])-1])]=[]

	value = []
	live_tex = []
	live_value=[]
	reviews=[]

	times=[]
	valuess=[]

	driver.get(url)
	# ("section-star-display")
	# ("section-rating-term").text  # 2 elements: # of reviews, # of dollars	
	value = driver.find_elements_by_class_name("section-popular-times-bar")
	live_tex = driver.find_elements_by_class_name("section-popular-times-live-description")
	live_value = driver.find_elements_by_class_name("section-popular-times-live-value")
	reviews=driver.find_element_by_xpath('//*[@id="pane"]/div/div[2]/div/div/div[1]/div[3]/div[2]/div/div[1]/span[3]/ul/li/span[2]/span[1]/button')
	info['g_#reviews']=reviews.text

	if len(live_tex) != 0:
		info['live_text'] = live_tex[0].text
		# text is an object of webElemenet
	if len(live_value) != 0:
		info['live_value'] = live_value[0].get_attribute("aria-label")
	
	for ele in range(len(value)):
		classname = value[ele].get_attribute("class")
		if classname.find("live") == -1:
			index_list=value[ele].get_attribute("aria-label").split(" busy at ")
			if len(index_list)==2 and 'M' in index_list[1]:
				times.append(re.sub(r' ','',index_list[1]))
				valuess.append(float(re.sub(r'%','',index_list[0])))
			if "Current" in str(value[ele].get_attribute("aria-label")):
				info['current_value'] = value[ele].get_attribute("aria-label") 
	
	numbers['time'].append([list(Counter(times).keys())[i].split('.')[0] for i in range(len(list(Counter(times).keys())))])
	
	for i in range(len(times)): #attach values to weekdays at the order from place detail API
		appeared=list(Counter(times[:i+1]).values())[list(Counter(times[:i+1]).keys()).index(times[i])]
		numbers[list(numbers.keys())[appeared]].append(valuess[i])

	# print(numbers)
	# print(info)			
	return[numbers,info]
	
for a in range(len(coorlist)):
	page=requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+coorlist[a]+"&radius=55&keyword=restaurant&key=AIzaSyCs9iFQSqVfgFtPhey4WB-zwHd5hhJPeYs")#key1=AIzaSyA4ZJTg8gVk9Dg4O_nI3LDCeXrZwXfaU2c  key2=AIzaSyCs9iFQSqVfgFtPhey4WB-zwHd5hhJPeYs
	tree=html.fromstring(page.content)

	stuff=tree.xpath('//body/p/text()')#stuff id list()
	stuff2=xmlify(stuff)#stuff2 becomes string
	stuff3=json.loads(stuff2)#stuff3 set to be json

	if len(stuff3['results']) != 0: 
		for b in range(len(stuff3['results'])): #gets all the nearby places
			days_list=[]
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
			allRes['g_rating'].append(stuff3['results'][b]['rating'])
			for c in range(len(stu3['result']['opening_hours']['periods'])):
				days_list.append(stu3['result']['opening_hours']['periods'][c]['open']['day'])
			try:
				allRes['g_open_now'].append(stuff3['results'][b]['opening_hours']['open_now'])
			except:
				allRes['g_open_now'].append("N/A")
			allRes['open_days'].append(days_list)			
# print(allRes)

for ele in range(len(allRes['url'])):
	temp=getIndexes(allRes['url'][ele],allRes['open_days'][ele])
	allRes['pop_numbers'].append(temp[0].copy())
	allRes['pop_info'].append(temp[1].copy())
	print(str(ele+1)+" Place(s) Scraped")
# getIndexes("https://maps.google.com/?cid=12777293506627589287") #for testing

try:
    for i in range(len(allRes['name'])):
    	temp=query_api(allRes['name'][i],allRes['lat'][i],allRes['lon'][i])
    	allRes['y_open_now'].append(temp['y_open_now'])
    	allRes['y_rating'].append(temp['y_rating'])
    	allRes['y_#reviews'].append(temp['y_#reviews'])
    	fig, ax=plt.subplots()
    	lege=[]
    	v=list(allRes['pop_numbers'][i].keys())[1:]
    	for j in range(len(v)):
    		lege.append(ax.bar(np.arange(18)+float(j/10),allRes['pop_numbers'][i].get(v[j]),width=0.1,color=co[j])[0])
    	ax.set_xticks(np.arange(18)+(len(list(allRes['pop_numbers'][i].keys())[1:])-1)/20)
    	ax.set_xticklabels(allRes['pop_numbers'][i]['time'][0])
    	ax.set_yticklabels(np.arange(0,120,20))
    	ax.set_title((allRes['name'][i]+
    		'\nYelp: '+re.search('[0-5][.][0-9]',str(allRes['y_rating'][i])).group(0)+' stars, '+re.search('\w+',str(allRes['y_#reviews'][i])).group(0)+' reviews'+
    		'\nGoogle Maps: '+str(allRes['g_rating'][i])+' stars, '+str(allRes['pop_info'][i]['g_#reviews'])))
    	ax.legend(lege,list(allRes['pop_numbers'][i].keys())[1:])
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
