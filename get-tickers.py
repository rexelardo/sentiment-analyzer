import urllib.request, json 
from jinja2 import Environment, FileSystemLoader
import pandas as pd

tickers = ''
price_df = {'tickers':[], 'price':[], "percent_change":[],\
    'market_cap':[], 'vol_24h':[], 'id':[]}
for i in range(1, 11):
    endpoint = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={i}&sparkline=false'

    with urllib.request.urlopen(endpoint) as url:
        data = json.loads(url.read().decode())
        for crypto in data:
            tickers = tickers + "'" + crypto['symbol'].upper() + "'" + ','
            price_df['tickers'].append(crypto['symbol'].upper())
            price_df['price'].append(crypto['current_price'])
            price_df['percent_change'].append(crypto['price_change_percentage_24h'])
            price_df['market_cap'].append(crypto['market_cap'])
            price_df['vol_24h'].append(crypto['total_volume'])
            price_df['id'].append(crypto['id'])
file_loader = FileSystemLoader('./')
env = Environment(loader=file_loader)
template = env.get_template('data.jinja2')
output = template.render(tickers=tickers)
with open("data.py", "w") as fh:
    fh.write(output)


prices = pd.DataFrame(price_df).set_index('tickers')
prices = prices.rename_axis(None)
prices.to_csv('prices.csv')