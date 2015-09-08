from trade_api.poe_trade_interface import POETradeInterface

interface = POETradeInterface()
search_args = { "type" : ["Bow"]}
print interface.get_query_url(search_args)
