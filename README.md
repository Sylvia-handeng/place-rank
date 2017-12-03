# place-rank
To scrape, visualize and rank places based on real-time traffic popularity, ratings and # of reviews by scraping data and accessing Google Maps and Yelp APIs

Completed:
getInfo.py scrapes places like restaurants from Google Maps for parameters like name, gps, ratings, # of reviews and most importantly - popular times;
then grabs info like ratings, # of reviews, open_now from Yelp for these places using yelp.py;
visualize the popular index by hour by weekday (6am to 11pm from Mon to Sun) in getInfo.py.

To be done:
scrape all restaurants in Manhattan then visualize popular indexes (including live index) on map;
rank nearby restaurants by combination of popularity level + ratings & # of reviews from Yelp & Google + location convenience
