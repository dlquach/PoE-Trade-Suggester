"""
An API for interfacing with poe.trade

Required features:
    - Programmatically query poe.trade's database just like you can via the actual website.
    - Sort responses from poe.trade
    - Get specific item information for display
"""

import urllib2
import re
import mechanize

from BeautifulSoup import BeautifulSoup
from tabulate import tabulate
from natsort import natsorted

# Sanitize bad HTML so mechanize doens't die
# Code found on StackOverflow 
class SanitizeHandler(mechanize.BaseHandler):
    def http_response(self, request, response):
        if not hasattr(response, "seek"):
            response = mechanize.response_seek_wrapper(response)
        if ( response.info().dict.has_key('content-type') and 
        ('html' in response.info().dict['content-type']) ):
            soup = BeautifulSoup(response.get_data())
            response.set_data(soup.prettify())
        return response

class POETradeInterface():
    def _init_browser(self):
        """
        Initializes and returns a Mechanize browser.
        """
        # Initialize the browser
        br = mechanize.Browser(factory=mechanize.RobustFactory())
        br.add_handler(SanitizeHandler())

        # Ignore the robots.txt
        br.set_handle_robots(False)

        return br

    def __init__(self):
        self._browser = self._init_browser()

    def get_query_url(self, search_args):
        """
        Queries poe.trade with the provided parameters and returns the corresponding
        poe.trade URL for the results.

        The argument types are based on the form as Mechanize sees the page. This requires
        very exact values. For example, setting the type as a bow would need a dict like so:
            {
                "type" : ["Bow"] 
            }
        
        Args:
            search_args (dict): dictionary containing search arguments

        Returns:
            string: the url for poe.trade

            Example output: "http://poe.trade/search/imakumakaugogo"
        """
        self._browser.open("http://poe.trade/")

        # There are two forms, the second one is the search form
        # Both forms don't have names so we just know the 2nd one is the right one
        self._browser.form = list(self._browser.forms())[1]

        # Populate the forms with the stuff we want
        for form_name in search_args:
            control = self._browser.form.find_control(form_name)
            control.value = search_args[form_name]

        # By default we want people are are online and accepting buyouts
        buyout_control = self._browser.form.find_control("buyout")
        online_control = self._browser.form.find_control("online")
        buyout_control.value = ["x"]
        online_control.value = ["x"]
        
        search_response = self._browser.submit()
        return search_response.geturl()
    
    def get_query_url_results(self, url):
        """
        Takes in a query and returns an array containing all of the item data.

        TODO: Return a dictionary instead of this ugly array
        """
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        page = response.read()
        soup = BeautifulSoup(page)

        headers = ["Item Name", "Seller IGN", "Sockets", "Price"]
        names = []
        sellers = []
        sockets = []
        prices = []

        # itemframe2 indicates a rare, itemframe3 indicates a unique
        name_search = soup.findAll("a", {"class" : ["title itemframe2", "title itemframe3"]})
        for item in name_search:
            raw_name = ''.join(item.findAll(text=True))
            if "corrupted" in raw_name:
                names.append(raw_name.replace("corrupted ", '') + '(C)')
            else:
                names.append(raw_name)

        price_search = soup.findAll("tbody", {"class" : "item"})
        for item in price_search:
            prices.append(item["data-buyout"])

        socket_search = soup.findAll("span", {"class" : "sockets-raw"})
        for item in socket_search:
            sockets.append(item.text)

        seller_search = soup.findAll("span", {"class" : "requirements"})

        for item in seller_search:
            find_ign = re.search('IGN:\ ([A-Za-z0-9_]*)\ ', item.text)
            if find_ign:
                sellers.append(find_ign.group(1))

        data = zip(names, sellers, sockets, prices)
        return data

    def _sort_by_price(self, data):
        """
        Sorts a given dataset by price (separating the currencies accordingly since we 
        don't have accurate exchange rate data). That is, sort numerically but split up
        currency types (alch < fusing < chaos < exalted).
        
        Args:
            array: in the form of [(<name>, <IGN>, <links>, <price>)]
        
        Returns:
            array: sorted version of the passed in array
        """
        # Separate the data by currency   
        alch = []
        fusing = []
        chaos = []
        exalted = []

        # We know that the item at index 3 is the price in the format of "# <currency>"
        for item in data:
            if "alchemy" in item[3]:
                alch.append(item)
            elif "fusing" in item[3]:
                fusing.append(item)
            elif "chaos" in item[3]:
                chaos.append(item)
            elif "exalted" in item[3]:
                exalted.append(item)

        alch = natsorted(alch, key=lambda item: item[3])
        fusing = natsorted(fusing, key=lambda item: item[3])
        chaos = natsorted(chaos, key=lambda item: item[3])
        exalted = natsorted(exalted, key=lambda item: item[3])

        result = []
        result.extend(alch)
        result.extend(fusing)
        result.extend(chaos)
        result.extend(exalted)
        return result
    
    def get_cheapest_query_results(self, url):
        """
        Takes in a query url, processes the results, and returns the top 5 cheapest items
        that match our criteria.
        
        Args:
            url (string): the url for the search we want to parse
        
        Returns:
            dict: items, their prices, and their stats 
        """
        data = self.get_query_url_results(url)
        data = self._sort_by_price(data)
        headers = ["Item Name", "Seller IGN", "Sockets", "Price"]
        print tabulate(data, headers, tablefmt="rst")

















