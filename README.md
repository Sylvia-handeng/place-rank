# place-rank
To scrape, visualize and rank Google places based on real-time traffic popularity, ratings and # of reviews by scraping data and accessing Google Maps and Yelp APIs

Completed:
getInfo.py scrapes places like restaurants from Google Maps for parameters like name, gps, ratings, # of reviews and most importantly - popular times;
then grabs info like ratings, # of reviews, open_now from Yelp for these places;
visualize the popular index by hour by weekday (6am to 11pm from Mon to Sat).

To be done:
scrape all restaurants in Manhattan then visualize popular indexes (including live index) on map;
rank nearby restaurants by combination of popularity level + ratings & # of reviews from Yelp & Google + location convenience
