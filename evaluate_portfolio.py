import plotly.graph_objects as go
from price_api.price_api import PriceAPIFactory
from portfolio_config import ASSETS


asset_prices = dict()
portfolio_results = dict()
portfolio_percentage = dict()

usd_pln_exchange_api = PriceAPIFactory.get_price_api('USDPLN')
usd_pln_exchange_price = usd_pln_exchange_api.get_price()
usd_pln_exchange_api.close()

print(f'USD/PLN: {usd_pln_exchange_price}')

for asset, value in ASSETS.items():
    price_api = PriceAPIFactory.get_price_api(asset)
    price = price_api.get_price()
    pln_price = round(price * usd_pln_exchange_price, 2)
    print(f'Asset: {asset}, price {price} $ ({pln_price} PLN)')

    asset_prices[asset] = price
    portfolio_results[asset] = round(pln_price * value, 2)

    price_api.close()


total_results = sum(portfolio_results.values())
portfolio_percentage = [f'{round((val / total_results) * 100, 2) } %' for val in portfolio_results.values()]

print(f'Portfolio results: {portfolio_results}')
print(f'Total (PLN): {total_results}')

# fig = go.Figure(
#     [go.Bar(
#         x=list(portfolio_results.keys()),
#         y=list(portfolio_results.values()),
#         text=portfolio_percentage)])
#
# fig.update_layout(
#     title=f'Total: {round(total_results, 2)} PLN',
#     xaxis_title='Assets',
#     yaxis_title='Sum (PLN)'
# )
#
# fig.show()



