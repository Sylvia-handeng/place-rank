from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib

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


def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    assert CLIENT_ID, "Please supply your client_id."
    assert CLIENT_SECRET, "Please supply your client_secret."
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token


def request(host, path, bearer_token, url_params=None):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(bearer_token, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)


def get_business(bearer_token, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, bearer_token)


def query_api(term, lat, lon):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)
    response = search(bearer_token, term, str(lat)+","+str(lon))
    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, lat, lon))
        return
    bus={}
    bus['name']=[]
    bus['lat']=[]
    bus['lon']=[]
    bus['open_now']=[]
    bus['rating']=[]
    bus['#reviews']=[]

    for i in range(len(businesses)):
        response = get_business(bearer_token, businesses[i]['id'])
        if term.split(' ')[0]==response['name'].split(' ').copy()[0] and round(float(lat),3)==round(float(response['coordinates']['latitude']),3) and round(float(lon),3)==round(float(response['coordinates']['longitude']),3):
            bus['name'].append(response['name'])
            bus['lat'].append(response['coordinates']['latitude'])
            bus['lon'].append(response['coordinates']['longitude'])
            bus['open_now'].append(response['hours'][0]['is_open_now'])
            bus['rating'].append(response['rating'])
            bus['#reviews'].append(response['review_count'])
    print(bus)

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
    #                     type=str, help='Search term (default: %(default)s)')
    # parser.add_argument('-l', '--location', dest='location',
    #                     default=DEFAULT_LOCATION, type=str,
    #                     help='Search location (default: %(default)s)')
    # input_values = parser.parse_args()
    # try:
    #     query_api(input_values.term, input_values.location)
    try:
        query_api(term,location)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )


if __name__ == '__main__':
    main()
