from trade_api.poe_trade_interface import POETradeInterface

interface = POETradeInterface()
search_args = {"type" : ["Bow"], "pdps_min" : "300"}
url = interface.get_query_url(search_args)
print url
interface.get_cheapest_query_results(url)
