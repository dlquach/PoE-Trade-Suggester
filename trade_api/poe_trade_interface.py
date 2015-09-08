"""
An API for interfacing with poe.trade

Required features:
    - Programmatically query poe.trade's database just like you can via the actual website.
    - Sort responses from poe.trade
    - Get specific item information for display
"""

from BeautifulSoup import BeautifulSoup
import mechanize

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
        browser = self._init_browser()
        browser.open("http://poe.trade/")

        # There are two forms, the second one is the search form
        # Both forms don't have names so we just know the 2nd one is the right one
        browser.form = list(browser.forms())[1]

        # Populate the forms with the stuff we want
        for form_name in search_args:
            control = browser.form.find_control(form_name)
            control.value = search_args[form_name]

        # By default we want people are are online and accepting buyouts
        buyout_control = browser.form.find_control("buyout")
        online_control = browser.form.find_control("online")
        buyout_control.value = ["x"]
        online_control.value = ["x"]
        
        search_response = browser.submit()
        return search_response.geturl()



















